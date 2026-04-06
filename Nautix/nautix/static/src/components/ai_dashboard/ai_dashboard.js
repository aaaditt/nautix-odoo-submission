/** @odoo-module **/

import { Component, useState, useRef, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class AIDashboard extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.action = useService("action");
        this.queryInput = useRef("query-input");
        
        this.state = useState({
            loading: false,
            matches: [],
            stats: {
                total_vessels: 12,
                available_vessels: 8,
                readyness: 98,
            }
        });

        onWillStart(async () => {
            await this._fetchStats();
        });
    }

    async _fetchStats() {
        const stats = await this.rpc("/web/dataset/call_kw/nautix.vessel/search_count", {
            model: "nautix.vessel",
            method: "search_count",
            args: [[['status', '=', 'available']]],
            kwargs: {},
        });
        this.state.stats.available_vessels = stats;
        
        const total = await this.rpc("/web/dataset/call_kw/nautix.vessel/search_count", {
            model: "nautix.vessel",
            method: "search_count",
            args: [[]],
            kwargs: {},
        });
        this.state.stats.total_vessels = total;
    }

    async _onAnalyze() {
        const prompt = this.queryInput.el.value;
        if (!prompt) return;

        this.state.loading = true;
        this.state.matches = [];

        try {
            // 1. Create the AI Query record
            const queryId = await this.rpc("/web/dataset/call_kw/nautix.ai.query/create", {
                model: "nautix.ai.query",
                method: "create",
                args: [{ prompt }],
                kwargs: {},
            });

            // 2. Call the analyze method
            await this.rpc(`/web/dataset/call_kw/nautix.ai.query/action_analyze`, {
                model: "nautix.ai.query",
                method: "action_analyze",
                args: [[queryId]],
                kwargs: {},
            });

            // 3. Get the results
            const [queryData] = await this.rpc("/web/dataset/call_kw/nautix.ai.query/read", {
                model: "nautix.ai.query",
                method: "read",
                args: [[queryId]],
                kwargs: { fields: ['results_json'] },
            });

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
