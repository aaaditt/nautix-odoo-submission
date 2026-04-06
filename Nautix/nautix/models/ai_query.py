from odoo import models, fields, api

class NautixAIQuery(models.Model):
    _name = 'nautix.ai.query'
    _description = 'Nautix AI Query'

    prompt = fields.Text(string='User Prompt', required=True)
    results_json = fields.Text(string='AI Analysis Result')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('processed', 'Processed'),
        ('failed', 'Failed')
    ], default='draft')
    charter_id = fields.Many2one('nautix.charter', string='Created Charter')

    def action_analyze(self):
        """
        AI ANALYSIS V2: Enhanced with Cargo Mapping, Port Matching, and Split-Ship logic.
        """
        import json
        import re
        from datetime import datetime, timedelta

        self.ensure_one()
        # Use read to avoid potential Odoo cache issues with unhashable types in some contexts
        res = self.read(['prompt'])
        prompt = (res[0].get('prompt') or "").lower()

        # 1. ENHANCED EXTRACTION
        quantity = 0
        match_qty = re.search(r'(\d+)\s*(?:k|ton|mt)', prompt)
        if match_qty:
            quantity = int(match_qty.group(1))
            if 'k' in match_qty.group(0):
                quantity *= 1000

        # Smart Cargo Mapping
        cargo_mapping = {
            'fuel': 'tanker', 'oil': 'tanker', 'crude': 'tanker', 'jet': 'tanker',
            'gas': 'lng', 'lng': 'lng',
            'grain': 'bulk_carrier', 'wheat': 'bulk_carrier', 'coal': 'bulk_carrier',
            'cars': 'roro', 'vehicles': 'roro',
        }
        detected_vessel_type = next((v for k, v in cargo_mapping.items() if k in prompt), False)

        # Fuzzy Port Extraction
        all_ports = self.env['nautix.port'].search([])
        load_port_id = False
        discharge_port_id = False
        
        # Simple extraction: find existing port names in the prompt
        found_ports = []
        for port in all_ports:
            if port.name.lower() in prompt:
                found_ports.append(port.id)
        
        if len(found_ports) >= 2:
            load_port_id = found_ports[0]
            discharge_port_id = found_ports[1]
        elif len(found_ports) == 1:
            load_port_id = found_ports[0]

        # 2. ADVANCED SEARCH
        # We now look for available vessels AND vessels that will be available soon (ETA < 14 days)
        vessels = self.env['nautix.vessel'].search([
            ('status', 'in', ['available', 'on_charter'])
        ])
        
        matches = []
        for vessel in vessels:
            score = 0
            reason_tags = []
            
            # -- Safety check on DWT and Capacity --
            vessel_dwt = vessel.dwt or 0.0
            if vessel_dwt < (quantity * 0.8): # Allow slightly smaller for split suggestions later
                continue
            
            # -- Base Score: Capacity Fit --
            fit_ratio = quantity / vessel_dwt if vessel_dwt > 0 else 0
            score += min(fit_ratio * 40, 40) # Up to 40 points for capacity fit

            # -- Bonus: Vessel Type Match --
            if detected_vessel_type:
                # Odoo selection values are technical names (strings)
                v_type = vessel.vessel_type or ""
                if v_type == detected_vessel_type:
                    score += 50
                    reason_tags.append("Optimal vessel type")
                else:
                    score -= 30
                    reason_tags.append("Type mismatch (Repurposing needed)")

            # -- Availability Logic --
            if vessel.status == 'available':
                score += 10
                reason_tags.append("Ready now")
            else:
                score -= 10
                reason_tags.append("In transit - check ETA")

            matches.append({
                'id': vessel.id,
                'name': vessel.name,
                'vessel_type': vessel.vessel_type or 'Unknown',
                'dwt': vessel.dwt,
                'score': min(max(round(score, 1), 0), 100),
                'reason': ", ".join(reason_tags),
                'load_port_id': load_port_id,
                'discharge_port_id': discharge_port_id,
            })

        # 3. SPLIT-SHIP CHECK
        if not any(m['score'] > 80 for m in matches) and quantity > 0:
            # If no single ship is perfect, suggest the two largest ships
            top_two = sorted(vessels, key=lambda x: (x.dwt or 0.0), reverse=True)[:2]
            if len(top_two) == 2 and ((top_two[0].dwt or 0.0) + (top_two[1].dwt or 0.0)) >= quantity:
                matches.append({
                    'id': False, # Complex match
                    'name': f"{top_two[0].name} + {top_two[1].name}",
                    'vessel_type': "Multi-Ship Squad",
                    'dwt': top_two[0].dwt + top_two[1].dwt,
                    'score': 95,
                    'reason': "Dual-ship split load (Highly efficient)",
                    'is_split': True,
                    'ship_ids': [top_two[0].id, top_two[1].id]
                })

        matches = sorted(matches, key=lambda x: x['score'], reverse=True)

        self.write({
            'results_json': json.dumps({
                'matches': matches[:5],
                'metadata': {
                    'load_port_id': load_port_id,
                    'discharge_port_id': discharge_port_id,
                    'quantity': quantity
                }
            }),
            'state': 'processed'
        })
        return True
