// # below are the ai chatbot frontend instructions and state management
/** @odoo-module **/
// below are the ai chatbot frontend instructions and state management

import { Component, useState, useRef, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class AIDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.queryInput = useRef("query-input");
        
        this.state = useState({
            loading: false,
            matches: [],
            metadata: {},
            stats: {
                total_vessels: 0,
                available_vessels: 0,
                readyness: 98,
            }
        });

        onWillStart(async () => {
            await this._fetchStats();
        });
    }

    async _fetchStats() {
        const availableCount = await this.orm.searchCount("nautix.vessel", [
            ['status', '=', 'available']
        ]);
        this.state.stats.available_vessels = availableCount;
        
        const totalCount = await this.orm.searchCount("nautix.vessel", []);
        this.state.stats.total_vessels = totalCount;
    }

    async _onAnalyze() {
        const prompt = this.queryInput.el.value;
        if (!prompt) return;

        this.state.loading = true;
        this.state.matches = [];

        try {
            // 1. Create the AI Query record
            const result = await this.orm.create("nautix.ai.query", [{ prompt }]);
            const queryId = Array.isArray(result) ? result[0] : result;

            // 2. Call the analyze method (pass as recordset IDs)
            await this.orm.call("nautix.ai.query", "action_analyze", [queryId]);

            // 3. Get the results (pass list of IDs)
            const queryDataList = await this.orm.read("nautix.ai.query", [queryId], ['results_json']);
            const queryData = queryDataList[0];

            if (queryData && queryData.results_json) {
                const data = JSON.parse(queryData.results_json);
                this.state.matches = data.matches || [];
                this.state.metadata = data.metadata || {};
            }

        } catch (error) {
            console.error("AI Analysis failed", error);
        } finally {
            this.state.loading = false;
        }
    }

    _onKeydown(ev) {
        if (ev.key === 'Enter') {
            this._onAnalyze();
        }
    }

    async _onCreateCharter(match) {
        const metadata = this.state.metadata || {};
        
        // Redirection logic with rich context (Ports, Quantity, Vessel)
        const context = {
            default_charter_type: 'voyage_charter',
            default_notes: `AI Logistics Assistant Recommendation\nMatch score: ${match.score}%\nReasoning: ${match.reason}`,
            default_cargo_quantity: metadata.quantity || match.dwt,
        };

        if (match.id) {
            context.default_vessel_id = match.id;
        }

        if (metadata.load_port_id) {
            context.default_load_port_ids = [[6, 0, [metadata.load_port_id]]];
        }
        if (metadata.discharge_port_id) {
            context.default_discharge_port_ids = [[6, 0, [metadata.discharge_port_id]]];
        }

        this.action.doAction({
            type: 'ir.actions.act_window',
            res_model: 'nautix.charter',
            views: [[false, 'form']],
            target: 'current',
            context: context
        });
    }
}

AIDashboard.template = "nautix.AIDashboard";

// Register the Client Action
registry.category("actions").add("nautix_ai_dashboard", AIDashboard);
