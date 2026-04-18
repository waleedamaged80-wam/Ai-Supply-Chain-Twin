"""
================================================================================
AI SUPPLY CHAIN TWIN
Multi-Echelon Inventory Optimization & Intelligent Scenario Planning
================================================================================

Copyright © 2026 Waleed A. Mageed. All Rights Reserved.

PROPRIETARY SOFTWARE - NOT FOR COMMERCIAL USE

This software is proprietary and confidential. Unauthorized reproduction,
distribution, modification, or commercial use is strictly prohibited and may
result in severe civil and criminal penalties.

PERMITTED USES:
• Educational purposes and personal study only
• Non-commercial research and evaluation
• Running on personal computer for testing

PROHIBITED USES:
• Commercial use of any kind
• Modification or creation of derivative works
• Distribution, sublicensing, or sharing with third parties
• Offering as a service (SaaS) or incorporating into commercial products
• Removal of copyright notices

COMMERCIAL LICENSING:
For commercial use, modifications, or distribution rights, contact:
  Waleed A. Mageed
  Email: waleed.amaged80@gmail.com
  LinkedIn: www.linkedin.com/in/waleed-abdel-mageed-cscp-pmp®-b283b316

Available licenses: Enterprise, SaaS, White-label, Custom development

THIRD-PARTY COMPONENTS:
This software uses open-source libraries (Streamlit, Pandas, NumPy, SciPy, 
Plotly), each governed by its respective license. The restrictions above apply 
only to the proprietary code developed by Waleed A. Mageed.

DEVELOPMENT ACKNOWLEDGMENT:
Developed with assistance from Claude (Anthropic AI Assistant).

WARRANTY DISCLAIMER:
This software is provided "AS IS" without warranty of any kind. Use at your
own risk. The author shall not be liable for any damages arising from the use
of this software.

For complete license terms, see LICENSE file.

Version: 1.2.5
Last Updated: April 8, 2026

================================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import re
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats
import json

# ============================================================
# CARBON FOOTPRINT CALCULATOR
# ============================================================

class CarbonFootprintCalculator:
    """Calculate carbon emissions for supply chain operations"""
    
    # Emission factors (based on DEFRA 2023, IMO 2023, IATA 2023)
    TRANSPORT_EMISSIONS = {
        'Truck': 62,      # g CO2 per ton-km
        'Train': 22,      # g CO2 per ton-km
        'Ship': 10,       # g CO2 per ton-km
        'Air': 500        # g CO2 per ton-km
    }
    
    WAREHOUSE_EMISSIONS = {
        'Ambient': 0.5,              # kg CO2 per unit per year
        'Refrigerated': 2.0,         # kg CO2 per unit per year
        'Frozen': 4.0,               # kg CO2 per unit per year
        'Climate-Controlled': 1.0    # kg CO2 per unit per year
    }
    
    @staticmethod
    def calculate_transport_co2(distance_km, weight_kg, units, mode='Truck'):
        """
        Calculate transport emissions
        
        Args:
            distance_km: Distance traveled
            weight_kg: Weight per unit
            units: Number of units transported
            mode: Transport mode (Truck/Train/Ship/Air)
        
        Returns:
            CO2 emissions in kg
        """
        emission_factor = CarbonFootprintCalculator.TRANSPORT_EMISSIONS.get(mode, 62)
        total_weight_tons = (weight_kg * units) / 1000
        emissions_g = distance_km * total_weight_tons * emission_factor
        return emissions_g / 1000  # Convert to kg
    
    @staticmethod
    def calculate_warehouse_co2(avg_inventory, days, storage_type='Ambient'):
        """
        Calculate warehouse emissions
        
        Args:
            avg_inventory: Average inventory level (units)
            days: Number of storage days
            storage_type: Type of storage facility
        
        Returns:
            CO2 emissions in kg
        """
        emission_factor = CarbonFootprintCalculator.WAREHOUSE_EMISSIONS.get(storage_type, 0.5)
        emissions = avg_inventory * (days / 365) * emission_factor
        return emissions
    
    @staticmethod
    def get_carbon_rating(carbon_intensity):
        """
        Get performance rating based on carbon intensity
        
        Args:
            carbon_intensity: kg CO2 per dollar of revenue
        
        Returns:
            tuple: (rating_text, stars, color)
        """
        if carbon_intensity < 0.05:
            return ("Excellent", "⭐⭐⭐", "#28a745")
        elif carbon_intensity < 0.10:
            return ("Good", "⭐⭐", "#2ECC71")
        elif carbon_intensity < 0.15:
            return ("Fair", "⭐", "#F39C12")
        else:
            return ("Poor", "❌", "#E74C3C")

# ============================================================
# 1. ADVANCED NLP SCENARIO PARSER
# ============================================================
class ScenarioParser:
    """Elite NLP engine for supply chain disruption scenarios"""
    
    DISRUPTION_PATTERNS = {
        'demand': {
            'increase': ['surge', 'spike', 'growth', 'increase', 'up', 'higher', 'jump', 'boom'],
            'decrease': ['drop', 'decline', 'decrease', 'down', 'lower', 'fall', 'reduction', 'slump'],
            'volatility': ['volatile', 'uncertain', 'unpredictable', 'fluctuating', 'erratic', 'unstable']
        },
        'supply': {
            'delay': ['delay', 'late', 'slow', 'postponed', 'extended lead time', 'backlog'],
            'disruption': ['strike', 'shutdown', 'closure', 'blocked', 'port congestion', 'lockout'],
            'quality': ['defect', 'quality issue', 'rejection', 'recall', 'rework']
        },
        'cost': {
            'increase': ['price increase', 'inflation', 'surcharge', 'premium', 'expensive'],
            'transport': ['freight cost', 'shipping cost', 'fuel surcharge', 'logistics cost']
        },
        'geography': ['port', 'suez', 'panama', 'shanghai', 'rotterdam', 'singapore', 'hong kong'],
        'urgency': ['critical', 'urgent', 'emergency', 'asap', 'immediate', 'crisis', 'rush', 'expedite', 'priority']
    }
    
    @staticmethod
    def parse(scenario_text):
        """Parse natural language scenario into structured disruption parameters"""
        text = scenario_text.lower()
        
        profile = {
            'demand_shift': 0,
            'demand_volatility': 1.0,
            'lead_time_shift': 0,
            'lead_time_variability': 0,
            'supplier_reliability': 100,
            'cost_multiplier': 1.0,
            'urgency': 'Normal',
            'scenario_type': 'baseline',
            'affected_nodes': [],
            'duration_days': 30
        }
        
        # Extract numerical values
        percentages = re.findall(r'(\d+)\s*%', text)
        days = re.findall(r'(\d+)\s*day', text)
        weeks = re.findall(r'(\d+)\s*week', text)
        
        # Demand analysis
        if any(word in text for word in ScenarioParser.DISRUPTION_PATTERNS['demand']['increase']):
            profile['demand_shift'] = int(percentages[0]) if percentages else 20
            profile['scenario_type'] = 'demand_surge'
        elif any(word in text for word in ScenarioParser.DISRUPTION_PATTERNS['demand']['decrease']):
            profile['demand_shift'] = -int(percentages[0]) if percentages else -15
            profile['scenario_type'] = 'demand_decline'
        
        if any(word in text for word in ScenarioParser.DISRUPTION_PATTERNS['demand']['volatility']):
            profile['demand_volatility'] = 2.0
        
        # Supply disruption analysis
        if any(word in text for word in ScenarioParser.DISRUPTION_PATTERNS['supply']['delay']):
            profile['lead_time_shift'] = int(days[0]) if days else (int(weeks[0])*7 if weeks else 5)
            profile['lead_time_variability'] = profile['lead_time_shift'] * 0.3
        
        if any(word in text for word in ScenarioParser.DISRUPTION_PATTERNS['supply']['disruption']):
            profile['supplier_reliability'] = 60
            profile['lead_time_variability'] = 3
            profile['scenario_type'] = 'supply_disruption'
            if 'strike' in text or 'shutdown' in text:
                profile['supplier_reliability'] = 30
        
        # Geographic impact
        if any(geo in text for geo in ScenarioParser.DISRUPTION_PATTERNS['geography']):
            profile['affected_nodes'] = ['Factory', 'Regional']
            profile['lead_time_shift'] += 7
        
        # Urgency classification
        if any(word in text for word in ScenarioParser.DISRUPTION_PATTERNS['urgency']):
            profile['urgency'] = 'Critical'
        
        # Duration
        if weeks:
            profile['duration_days'] = int(weeks[-1]) * 7
        elif 'month' in text:
            months = re.findall(r'(\d+)\s*month', text)
            profile['duration_days'] = int(months[0]) * 30 if months else 30
        
        return profile

# ============================================================
# 2. ENTERPRISE SUPPLY CHAIN SIMULATOR
# ============================================================
class SupplyChainTwin:
    """Digital twin of multi-echelon supply chain with realistic constraints"""
    
    def __init__(self, config):
        self.config = config
        
    def calculate_optimal_safety_stock(self, mean_demand, std_demand, lead_time, service_level):
        """Calculate safety stock using standard formula: z × σ_d × √LT"""
        z_score = stats.norm.ppf(service_level / 100)
        safety_stock = z_score * std_demand * np.sqrt(lead_time)
        return int(safety_stock)
    
    def calculate_eoq(self, annual_demand, ordering_cost, holding_cost_rate, unit_cost):
        """Economic Order Quantity"""
        if holding_cost_rate * unit_cost == 0:
            return 5000
        eoq = np.sqrt((2 * annual_demand * ordering_cost) / (holding_cost_rate * unit_cost))
        return int(eoq)
    
    def simulate_scenario(self, disruption_profile, sim_days=90, iterations=50):
        """Run Monte Carlo simulation with disruption scenario"""
        
        results = []
        daily_traces = {f"iter_{i}": [] for i in range(min(5, iterations))}
        
        # Economic parameters
        UNIT_COST = self.config.get('unit_cost', 100)
        MARGIN = self.config.get('margin', 50)
        HOLDING_COST_RATE = self.config.get('holding_rate', 0.25) / 365
        STOCKOUT_PENALTY = self.config.get('penalty', 200)
        TRANSPORT_COST = self.config.get('transport_cost', 2)
        ORDERING_COST = 500
        
        # Network configuration
        base_mean_demand = self.config.get('mean_demand', 535)
        base_std_demand = self.config.get('std_demand', 50)
        
        # Use single total lead time for all routes
        total_lead_time = self.config.get('lead_time', 10)
        base_lead_time = {
            'Factory_to_Regional': total_lead_time,
            'Regional_to_Local': max(1, int(total_lead_time * 0.2))  # 20% of total for local
        }
        
        # Apply disruption to parameters
        disrupted_mean = base_mean_demand * (1 + disruption_profile['demand_shift'] / 100)
        disrupted_std = base_std_demand * disruption_profile['demand_volatility']
        
        for iteration in range(iterations):
            # Initialize inventory positions
            inventory = {
                'Factory': 100000,
                'Regional': self.config.get('safety_stock', 15000) * 2,
                'Local': self.config.get('safety_stock', 15000)
            }
            
            pipeline = []
            daily_kpis = []
            cumulative_revenue = 0
            cumulative_costs = 0
            lost_sales = 0
            total_demand = 0
            
            for day in range(1, sim_days + 1):
                # --- RECEIVE PIPELINE ORDERS ---
                arrived_orders = [o for o in pipeline if o['arrival_day'] <= day]
                for order in arrived_orders:
                    inventory[order['destination']] += order['quantity']
                    pipeline.remove(order)
                
                # --- GENERATE DAILY DEMAND ---
                daily_demand = max(0, np.random.normal(disrupted_mean, disrupted_std))
                total_demand += daily_demand
                
                # --- FULFILL DEMAND from Local DC ---
                fulfilled = min(inventory['Local'], daily_demand)
                inventory['Local'] -= fulfilled
                shortage = daily_demand - fulfilled
                lost_sales += shortage
                
                # --- FINANCIAL ACCOUNTING ---
                revenue = fulfilled * (UNIT_COST + MARGIN)
                holding_costs = sum(inventory.values()) * UNIT_COST * HOLDING_COST_RATE
                stockout_costs = shortage * STOCKOUT_PENALTY
                
                cumulative_revenue += revenue
                cumulative_costs += (holding_costs + stockout_costs)
                
                # --- REPLENISHMENT LOGIC with (s,Q) Policy ---
                
                # Local DC orders from Regional
                local_position = inventory['Local'] + sum(o['quantity'] for o in pipeline if o['destination'] == 'Local')
                local_reorder_point = self.config.get('reorder_point_local', disrupted_mean * 3)
                
                if local_position < local_reorder_point:
                    order_qty = self.config.get('order_qty', 5000)
                    available_at_regional = inventory['Regional']
                    actual_ship = min(available_at_regional, order_qty)
                    
                    if actual_ship > 0:
                        inventory['Regional'] -= actual_ship
                        
                        base_lt = base_lead_time['Regional_to_Local']
                        lt_variance = np.random.normal(0, disruption_profile['lead_time_variability'])
                        actual_lt = max(1, int(base_lt + lt_variance))
                        
                        pipeline.append({
                            'quantity': actual_ship,
                            'destination': 'Local',
                            'arrival_day': day + actual_lt,
                            'cost': actual_ship * TRANSPORT_COST
                        })
                        cumulative_costs += actual_ship * TRANSPORT_COST
                
                # Regional DC orders from Factory
                regional_position = inventory['Regional'] + sum(o['quantity'] for o in pipeline if o['destination'] == 'Regional')
                regional_reorder_point = self.config.get('safety_stock', 15000)
                
                if regional_position < regional_reorder_point:
                    order_qty_regional = self.config.get('order_qty', 5000) * 5
                    
                    # Supplier reliability factor
                    if np.random.uniform(0, 100) < disruption_profile['supplier_reliability']:
                        available_at_factory = inventory['Factory']
                        actual_ship = min(available_at_factory, order_qty_regional)
                        
                        if actual_ship > 0:
                            inventory['Factory'] -= actual_ship
                            
                            base_lt = base_lead_time['Factory_to_Regional']
                            disrupted_lt = base_lt + disruption_profile['lead_time_shift']
                            lt_variance = np.random.normal(0, disruption_profile['lead_time_variability'])
                            actual_lt = max(1, int(disrupted_lt + lt_variance))
                            
                            pipeline.append({
                                'quantity': actual_ship,
                                'destination': 'Regional',
                                'arrival_day': day + actual_lt,
                                'cost': actual_ship * TRANSPORT_COST * 2
                            })
                            cumulative_costs += (actual_ship * TRANSPORT_COST * 2 + ORDERING_COST)
                
                # --- RECORD DAILY STATE ---
                daily_kpis.append({
                    'day': day,
                    'inventory_local': inventory['Local'],
                    'inventory_regional': inventory['Regional'],
                    'inventory_factory': inventory['Factory'],
                    'pipeline': sum(o['quantity'] for o in pipeline),
                    'demand': daily_demand,
                    'fulfilled': fulfilled,
                    'shortage': shortage,
                    'service_level': 100 * fulfilled / daily_demand if daily_demand > 0 else 100
                })
                
                if iteration < 5:
                    daily_traces[f"iter_{iteration}"].append({
                        'day': day,
                        'local': inventory['Local'],
                        'regional': inventory['Regional'],
                        'pipeline': sum(o['quantity'] for o in pipeline)
                    })
            
            # --- ITERATION SUMMARY ---
            overall_service_level = 100 * (1 - lost_sales / total_demand) if total_demand > 0 else 100
            net_profit = cumulative_revenue - cumulative_costs
            avg_inventory = np.mean([kpi['inventory_local'] + kpi['inventory_regional'] for kpi in daily_kpis])
            inventory_turns = (total_demand * UNIT_COST) / (avg_inventory * UNIT_COST) if avg_inventory > 0 else 0
            
            results.append({
                'iteration': iteration,
                'profit': net_profit,
                'revenue': cumulative_revenue,
                'total_costs': cumulative_costs,
                'service_level': overall_service_level,
                'lost_sales': lost_sales,
                'inventory_turns': inventory_turns,
                'avg_inventory': avg_inventory,
                'daily_kpis': daily_kpis
            })
        
        return pd.DataFrame(results), daily_traces

# ============================================================
# 3. AI DECISION ENGINE
# ============================================================
class DecisionEngine:
    """AI-powered decision support system"""
    
    @staticmethod
    def calculate_risk_score(results_df, target_service, mean_demand):
        """Multi-dimensional risk scoring"""
        avg_service = results_df['service_level'].mean()
        profit_volatility = results_df['profit'].std() / abs(results_df['profit'].mean()) if results_df['profit'].mean() != 0 else 0
        avg_lost_sales = results_df['lost_sales'].mean()
        
        risk_components = {
            'service_gap': max(0, target_service - avg_service) * 10,  # 0-100 scale
            'profit_volatility': min(100, profit_volatility * 100),     # 0-100 scale
            'stockout_cost': min(100, (avg_lost_sales / (mean_demand * 30)) * 200)  # 0-100 scale
        }
        
        # Weighted risk score
        total_risk = (
            risk_components['service_gap'] * 0.5 +
            risk_components['profit_volatility'] * 0.3 +
            risk_components['stockout_cost'] * 0.2
        )
        
        if total_risk > 60:
            risk_level = "Critical"
        elif total_risk > 30:
            risk_level = "Medium"
        else:
            risk_level = "Low"
        
        return {
            'total_risk': total_risk,
            'risk_level': risk_level,
            'components': risk_components
        }
    
    @staticmethod
    def analyze_performance(results_df, baseline_profit, target_service, mean_demand):
        """Generate intelligent insights and recommendations"""
        
        avg_profit = results_df['profit'].mean()
        avg_service = results_df['service_level'].mean()
        profit_volatility = results_df['profit'].std()
        
        insights = []
        recommendations = []
        
        # Risk assessment
        risk_analysis = DecisionEngine.calculate_risk_score(results_df, target_service, mean_demand)
        risk_level = risk_analysis['risk_level']
        
        # Performance gap analysis
        if avg_service < target_service:
            gap = target_service - avg_service
            insights.append(f"⚠️ Service level shortfall: {gap:.1f}% below target")
            
            # Calculate required safety stock increase
            current_ss_implicit = results_df['avg_inventory'].mean() * 0.3  # rough estimate
            required_increase = gap * current_ss_implicit * 0.02
            
            recommendations.append({
                'action': f'Increase Safety Stock by ~{required_increase:.0f} units',
                'impact': f'Estimated to improve service by {gap * 0.7:.1f}%',
                'cost': f'${required_increase * 100 * 0.25:.0f}/year in additional holding costs',
                'priority': 'High'
            })
        
        # Profit analysis
        if baseline_profit and avg_profit < baseline_profit * 0.9:
            profit_decline = ((baseline_profit - avg_profit)/baseline_profit * 100)
            insights.append(f"📉 Profit declined {profit_decline:.1f}% vs baseline")
            recommendations.append({
                'action': 'Optimize Order Quantities (EOQ Analysis)',
                'impact': 'Reduce transportation and ordering costs by 10-15%',
                'cost': 'Minimal - process change only',
                'priority': 'Medium'
            })
        
        # Volatility assessment
        coefficient_of_variation = profit_volatility / avg_profit if avg_profit != 0 else 0
        if coefficient_of_variation > 0.3:
            insights.append("📊 High profit volatility detected - supply chain is unstable")
            recommendations.append({
                'action': 'Dual-Source Strategy',
                'impact': 'Reduce dependency on single supplier, stabilize profit',
                'cost': 'Supplier qualification and management overhead',
                'priority': 'High' if risk_level == 'Critical' else 'Medium'
            })
        
        # Inventory efficiency
        avg_turns = results_df['inventory_turns'].mean()
        if avg_turns < 6:
            insights.append(f"💰 Inventory turns below industry benchmark ({avg_turns:.1f} vs 10+ target)")
            recommendations.append({
                'action': 'Implement VMI (Vendor Managed Inventory)',
                'impact': 'Improve turns by 30-40%, free up working capital',
                'cost': 'IT integration with suppliers ($25k-50k)',
                'priority': 'Low'
            })
        
        # Critical risk scenarios
        if risk_level == 'Critical':
            insights.append("🚨 CRITICAL: Supply chain at high risk of failure")
            recommendations.insert(0, {
                'action': 'Emergency Sourcing Activation',
                'impact': 'Immediate capacity injection, prevent stockouts',
                'cost': '20-30% premium on emergency orders',
                'priority': 'Critical'
            })
        
        return {
            'insights': insights,
            'recommendations': recommendations,
            'risk_analysis': risk_analysis,
            'key_metrics': {
                'avg_profit': avg_profit,
                'avg_service': avg_service,
                'profit_volatility': profit_volatility,
                'avg_turns': avg_turns
            }
        }
    
    @staticmethod
    def generate_executive_directive(analysis, disruption_profile):
        """Generate clear executive action directive"""
        risk_level = analysis['risk_analysis']['risk_level']
        avg_service = analysis['key_metrics']['avg_service']
        
        if risk_level == 'Critical':
            return {
                'status': '🔴 CRITICAL',
                'directive': 'IMMEDIATE ACTION REQUIRED: Activate emergency protocols',
                'primary_action': analysis['recommendations'][0]['action'] if analysis['recommendations'] else 'Review inventory policy',
                'timeline': 'Within 24 hours'
            }
        elif risk_level == 'Medium':
            return {
                'status': '🟡 CAUTION',
                'directive': 'Strategic adjustment needed to prevent escalation',
                'primary_action': analysis['recommendations'][0]['action'] if analysis['recommendations'] else 'Optimize inventory levels',
                'timeline': 'Within 1 week'
            }
        else:
            return {
                'status': '🟢 STABLE',
                'directive': 'Maintain current policy, monitor for changes',
                'primary_action': 'Continue monitoring performance metrics',
                'timeline': 'Standard review cycle'
            }

# ============================================================
# 4. SKU PORTFOLIO ANALYZER
# ============================================================
class PortfolioAnalyzer:
    """Analyze and optimize across multiple SKUs"""
    
    @staticmethod
    def classify_abc(sku_metrics):
        """ABC classification based on revenue contribution"""
        total_revenue = sum(m['revenue'] for m in sku_metrics.values())
        
        # Sort SKUs by revenue
        sorted_skus = sorted(sku_metrics.items(), key=lambda x: x[1]['revenue'], reverse=True)
        
        cumulative = 0
        classifications = {}
        
        for sku, metrics in sorted_skus:
            revenue_pct = (metrics['revenue'] / total_revenue * 100) if total_revenue > 0 else 0
            cumulative += revenue_pct
            
            if cumulative <= 70:
                class_label = 'A'
                importance = 'Critical'
            elif cumulative <= 95:
                class_label = 'B'
                importance = 'Important'
            else:
                class_label = 'C'
                importance = 'Standard'
            
            classifications[sku] = {
                'class': class_label,
                'importance': importance,
                'revenue_contribution': revenue_pct
            }
        
        return classifications
    
    @staticmethod
    def portfolio_risk_assessment(sku_results):
        """Assess risk across entire SKU portfolio"""
        critical_skus = []
        medium_risk_skus = []
        healthy_skus = []
        
        for sku, result in sku_results.items():
            risk_level = result['analysis']['risk_analysis']['risk_level']
            if risk_level == 'Critical':
                critical_skus.append(sku)
            elif risk_level == 'Medium':
                medium_risk_skus.append(sku)
            else:
                healthy_skus.append(sku)
        
        portfolio_health = {
            'critical_count': len(critical_skus),
            'medium_count': len(medium_risk_skus),
            'healthy_count': len(healthy_skus),
            'total_skus': len(sku_results),
            'portfolio_status': 'Critical' if critical_skus else ('Medium' if medium_risk_skus else 'Healthy')
        }
        
        return portfolio_health, critical_skus, medium_risk_skus, healthy_skus

# ============================================================
# 5. STREAMLIT INTERFACE WITH MULTI-SKU SUPPORT
# ============================================================
def main():
    st.set_page_config(page_title="AI Supply Chain Twin - Enterprise", layout="wide", page_icon="🧬")
    
    # Custom CSS
    st.markdown("""
        <style>
        .big-metric { font-size: 2.5rem; font-weight: bold; }
        .critical-status { color: #dc3545; font-weight: bold; font-size: 1.2rem; }
        .medium-status { color: #ffc107; font-weight: bold; font-size: 1.2rem; }
        .healthy-status { color: #28a745; font-weight: bold; font-size: 1.2rem; }
        .insight-box { background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #1f77b4; margin: 0.5rem 0; }
        .recommendation { background-color: #d4edda; padding: 0.8rem; margin: 0.5rem 0; border-radius: 0.3rem; border-left: 3px solid #28a745; }
        .recommendation-high { background-color: #fff3cd; border-left: 3px solid #ffc107; }
        .recommendation-critical { background-color: #f8d7da; border-left: 3px solid #dc3545; }
        .sku-card { background-color: white; padding: 1rem; border-radius: 0.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin: 0.5rem 0; }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("🧬 AI Supply Chain Twin — Enterprise Command Center")
    st.markdown("**Multi-SKU Portfolio Optimization • Intelligent Scenario Planning • Predictive Analytics**")
    
    # ============================================================
    # SIDEBAR: Configuration & Data Upload
    # ============================================================
    with st.sidebar:
        st.header("📂 Data Center")
        uploaded_file = st.file_uploader("Upload Master Data CSV", type="csv", help="CSV with SKU-level demand data")
    
    # Check if data uploaded (outside sidebar to be accessible everywhere)
    data_uploaded = uploaded_file is not None
    
    with st.sidebar:
        if not data_uploaded:
            st.info("📤 Please upload your Master Data CSV to begin analysis.")
            st.markdown("**Required columns:**")
            st.markdown("- Item/SKU identifier")
            st.markdown("- Historical demand/sales data")
        
    # If data uploaded, process it
    if data_uploaded:
        with st.sidebar:
            # Load data with encoding fallback
            try:
                df = pd.read_csv(uploaded_file, sep=None, engine='python', encoding='utf-8')
            except:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, sep=None, engine='python', encoding='ISO-8859-1')
            
            df.columns = [str(c).strip() for c in df.columns]
            
            st.success(f"✅ Loaded {len(df)} records")
            
            # Column mapping
            st.subheader("🗂️ Column Mapping")
            item_col = st.selectbox("Item/SKU ID Column:", df.columns, help="Column containing SKU identifiers")
            sales_col = st.selectbox("Demand/Sales Column:", df.columns, help="Column with historical demand data")
            
            # SKU selection
            all_items = df[item_col].unique()
            st.subheader("📦 SKU Selection")
            
            selection_mode = st.radio("Selection Mode:", ["Multi-Select", "ABC Classification"])
            
            if selection_mode == "Multi-Select":
                selected_items = st.multiselect(
                    "Select SKUs to Analyze:",
                    all_items,
                    default=all_items[:min(3, len(all_items))],
                    help="Choose specific SKUs for detailed analysis"
                )
            else:
                # ABC classification based on total demand
                sku_totals = {}
                for item in all_items:
                    item_data = df[df[item_col] == item]
                    raw_demand = pd.to_numeric(
                        item_data[sales_col].astype(str).str.replace(',', ''),
                        errors='coerce'
                    ).dropna()
                    sku_totals[item] = raw_demand.sum() if not raw_demand.empty else 0
                
                total_demand = sum(sku_totals.values())
                sorted_skus = sorted(sku_totals.items(), key=lambda x: x[1], reverse=True)
                
                cumulative = 0
                abc_classification = {}
                for sku, demand in sorted_skus:
                    pct = (demand / total_demand * 100) if total_demand > 0 else 0
                    cumulative += pct
                    if cumulative <= 70:
                        abc_classification[sku] = 'A'
                    elif cumulative <= 95:
                        abc_classification[sku] = 'B'
                    else:
                        abc_classification[sku] = 'C'
                
                class_filter = st.multiselect(
                    "Select ABC Classes:",
                    ['A', 'B', 'C'],
                    default=['A', 'B'],
                    help="A: Top 70% revenue, B: Next 25%, C: Bottom 5%"
                )
                
                selected_items = [sku for sku, cls in abc_classification.items() if cls in class_filter]
            
            if not selected_items:
                st.warning("⚠️ No SKUs selected. Please select at least one SKU.")
                selected_items = []  # Empty list instead of stopping
            else:
                st.info(f"🎯 Analyzing {len(selected_items)} SKU(s)")
            
            st.divider()
            
            # Global simulation settings
            st.subheader("⚙️ Simulation Settings")
            sim_days = st.slider("Simulation Horizon (days)", 30, 180, 90, 30)
            iterations = st.slider("Monte Carlo Iterations", 20, 100, 50, 10)
            target_service = st.slider("Target Service Level (%)", 85, 99, 95, 1)
            
            st.divider()
    else:
        # No data uploaded - set defaults for User Guide display
        selected_items = []
        df = None
        item_col = None
        sales_col = None
        sim_days = 90
        iterations = 50
        target_service = 95
    
    # ============================================================
    # MAIN INTERFACE: Portfolio Dashboard + Individual SKU Analysis
    # ============================================================
    
    # Initialize session state for all SKUs
    if 'sku_results' not in st.session_state:
        st.session_state['sku_results'] = {}
    
    # ============================================================
    # TAB 1: PORTFOLIO DASHBOARD
    # ============================================================
    tab_guide, tab_portfolio, *tab_skus = st.tabs(["📖 User Guide", "📊 Portfolio Dashboard"] + [f"📦 {item}" for item in selected_items])
    
    # ============================================================
    # USER GUIDE TAB
    # ============================================================
    with tab_guide:
        st.header("📖 User Guide - How to Use AI Supply Chain Twin")
        
        st.markdown("""
        Welcome to the **AI Supply Chain Twin**! This guide will help you optimize your inventory policies 
        and test disruption scenarios using advanced Monte Carlo simulation.
        """)
        
        # Quick Start
        with st.expander("🚀 Quick Start (5 Minutes)", expanded=True):
            st.markdown("""
            ### Step-by-Step Getting Started
            
            **1. Upload Your Data** 📤
            - Click **"Browse files"** in the sidebar
            - Upload a CSV file with SKU and demand data
            - Example columns: `SKU_ID`, `Sales`, `Date`, `Location`
            
            **2. Map Your Columns** 🗂️
            - Select which column contains **SKU/Product IDs**
            - Select which column contains **Demand/Sales data**
            
            **3. Choose SKUs** 📦
            - **Multi-Select**: Pick specific products to analyze
            - **ABC Classification**: Auto-select top performers
            - Start with 2-3 SKUs for your first run
            
            **4. Set Simulation Parameters** ⚙️
            - **Simulation Horizon**: 30-180 days (default: 90)
            - **Monte Carlo Iterations**: 20-100 (default: 50, more = more accurate)
            - **Target Service Level**: Your goal (default: 95%)
            
            **5. Configure Each SKU** 📊
            - Go to individual SKU tabs (e.g., "📦 Product A")
            - Review **Historical Demand** statistics
            - Set **Inventory Policy** parameters
            - Set **Cost & Pricing** details
            - Click **"▶️ Run Simulation"**
            
            **6. Review Results** 🎯
            - See **Performance Metrics** (profit, service level, turns)
            - Review **AI Insights & Recommendations**
            - Check **Risk Score** (0-100 scale)
            - View **Charts** (profit distribution, inventory dynamics)
            
            **7. View Portfolio** 🌐
            - Switch to **"Portfolio Dashboard"** tab
            - See combined performance across all analyzed SKUs
            - Compare SKUs side-by-side
            - Identify critical risks
            """)
        
        # Understanding Outputs
        with st.expander("📊 Understanding Your Results"):
            st.markdown("""
            ### Key Metrics Explained
            
            #### 💰 Average Profit
            - **What it is**: Expected profit over the simulation period
            - **How calculated**: Revenue - (Holding + Stockout + Transport costs)
            - **Good result**: Positive and stable (low ± variation)
            - **What to do**: If negative, check unit costs vs selling price
            
            #### 📈 Service Level
            - **What it is**: % of customer demand fulfilled
            - **How calculated**: (Fulfilled units / Total demand) × 100
            - **Good result**: ≥ 95% (meets or exceeds target)
            - **What to do**: If low, increase safety stock or reduce lead time
            
            #### 🔄 Inventory Turns
            - **What it is**: How many times you sell through inventory per year
            - **How calculated**: (Total demand × unit cost) / Average inventory value
            - **Good result**: 5-15x for most products (varies by industry)
            - **What to do**: If low (<3), reduce safety stock; if high (>20), may risk stockouts
            
            #### ⚠️ Avg Lost Sales
            - **What it is**: Average units NOT fulfilled due to stockouts
            - **Good result**: 0-5 units per simulation
            - **What to do**: If high, increase safety stock or order quantities
            
            #### 🎯 Risk Score (0-100)
            - **What it is**: Multi-factor risk assessment
            - **Components**:
              - Service gap (50%): How far below target
              - Profit volatility (30%): How unstable profits are
              - Stockout cost (20%): Financial impact of shortages
            - **Scale**:
              - 0-30: 🟢 Low Risk (Healthy)
              - 30-60: 🟡 Medium Risk (Monitor)
              - 60-100: 🔴 Critical Risk (Action needed)
            """)
        
        # Parameter Configuration
        with st.expander("⚙️ Configuring Parameters"):
            st.markdown("""
            ### Inventory Policy Parameters
            
            #### 📅 Lead Time (days)
            - **What it is**: Time from ordering to receiving inventory
            - **Default**: Calculated from your data
            - **How to set**: Use actual supplier lead times
            - **Impact**: Higher lead time = more safety stock needed
            
            #### 📦 Safety Stock (units)
            - **What it is**: Buffer inventory to prevent stockouts
            - **Formula**: 1.65 × σ × √(lead_time)
            - **How to adjust**: 
              - Increase if service level too low
              - Decrease if inventory turns too low
            
            #### 📊 Order Quantity (units)
            - **What it is**: How much to order each time
            - **Default**: Based on demand variability
            - **How to adjust**: Balance ordering costs vs holding costs
            
            #### 🎯 Reorder Point (units)
            - **What it is**: When inventory drops to this level, order more
            - **Formula**: Demand × (Lead time × 50%)
            - **How to adjust**: Set above safety stock
            
            ### Cost & Pricing Parameters
            
            #### 💵 Unit Cost ($)
            - **What it is**: What you pay per unit from supplier
            - **How to set**: Use actual procurement costs
            - **Can be**: $0.01 to $10,000+ (any decimal value)
            
            #### 💰 Profit Margin (%)
            - **What it is**: Markup percentage on unit cost
            - **Example**: 50% margin on $100 cost = $150 selling price
            - **How to set**: Use target margins from pricing strategy
            
            #### 📈 Holding Cost Rate (% per year)
            - **What it is**: Cost of storing inventory (% of value)
            - **Typical**: 15-30% per year
            - **Includes**: Warehouse, insurance, obsolescence, capital costs
            
            #### ⚠️ Stockout Penalty ($)
            - **What it is**: Cost per unit of lost sale
            - **Includes**: Lost profit + customer dissatisfaction
            - **Typical**: 2-5× unit profit margin
            
            #### 🚚 Transport Cost ($/unit)
            - **What it is**: Shipping cost per unit
            - **How to set**: Calculate from freight invoices
            """)
        
        # Scenario Planning
        with st.expander("🎯 Scenario Planning & Testing"):
            st.markdown("""
            ### How to Test Disruption Scenarios
            
            Each SKU has a **"Scenario Planning"** section where you can describe disruptions 
            in natural language. The AI will parse and simulate them.
            
            #### Example Scenarios:
            
            **Demand Disruptions:**
            - "Demand surge 30% for 3 weeks"
            - "Sales spike 50% next month"
            - "Demand increase 20% starting week 2"
            
            **Supply Disruptions:**
            - "Factory delay 10 days"
            - "Port strike 2 weeks"
            - "Supplier capacity reduced 40%"
            
            **Combined:**
            - "Demand surge 25% with factory delay 7 days"
            - "Holiday rush 60% increase but supplier unreliable"
            
            #### What the AI Does:
            1. **Parses** your scenario text
            2. **Extracts** key parameters (%, days, timing)
            3. **Adjusts** simulation accordingly
            4. **Runs** Monte Carlo with disruption
            5. **Compares** to baseline performance
            6. **Recommends** actions to take
            
            #### AI Decision Output:
            You'll see:
            - 🟢 **STABLE**: Maintain current policy
            - 🟡 **CAUTION**: Monitor closely, prepare adjustments
            - 🔴 **CRITICAL**: Take immediate action
            
            Plus specific recommendations like:
            - "Increase safety stock by 30%"
            - "Expedite next order"
            - "Negotiate backup supplier"
            """)
        
        # Multi-Echelon Network
        with st.expander("🏭 Understanding the Multi-Echelon Network"):
            st.markdown("""
            ### 3-Echelon Supply Chain Structure
            
            Your simulation models a realistic multi-level supply network:
            
            ```
            🏭 FACTORY (Supplier)
                │
                │ Lead Time: Your configured time (e.g., 10 days)
                │ Capacity: 100,000 units
                │ Transport: $4/unit
                ↓
            🏢 REGIONAL DC (Distribution Center)
                │
                │ Lead Time: 20% of total (e.g., 2 days)
                │ Inventory: 2× safety stock
                │ Transport: $2/unit
                ↓
            🏪 LOCAL STORE (Point of Sale)
                │
                │ Inventory: 1× safety stock
                │ Fulfills: Customer demand immediately
                ↓
            👥 CUSTOMERS (End demand)
            ```
            
            #### How It Works:
            
            **Daily Cycle:**
            1. Customer demand arrives at Local Store
            2. Local fulfills from inventory (or stockout)
            3. If Local inventory low → orders from Regional
            4. If Regional inventory low → orders from Factory
            5. In-transit orders arrive after lead time
            6. Costs calculated across ALL levels
            
            #### Benefits:
            - **Realistic modeling** (not single warehouse)
            - **Pipeline tracking** (in-transit inventory)
            - **Cascading effects** (disruptions propagate)
            - **Multi-level costs** (holding at each echelon)
            
            #### Costs Include:
            - Holding costs at Factory, Regional, AND Local
            - Transport costs between levels
            - Stockout penalties at customer-facing level
            """)
        
        # Carbon Footprint Tracking - NEW!
        with st.expander("🌱 Carbon Footprint Tracking (NEW!)"):
            st.markdown("""
            ### Understanding Carbon Footprint Analysis
            
            AI Supply Chain Twin now tracks the environmental impact of your supply chain operations!
            
            #### What Gets Measured:
            
            **🚛 Transport Emissions:**
            - **Factory → DC:** Primary transport (often long distance)
            - **DC → Store:** Last-mile delivery (often shorter distance)
            - **4 Transport Modes:**
              - Truck: 62 g CO2/ton-km (DEFRA 2023)
              - Train: 22 g CO2/ton-km (DEFRA 2023)
              - Ship: 10 g CO2/ton-km (IMO 2023)
              - Air: 500 g CO2/ton-km (IATA 2023)
            
            **🏭 Warehouse Emissions:**
            - **4 Storage Types:**
              - Ambient: 0.5 kg CO2/unit/year
              - Refrigerated: 2.0 kg CO2/unit/year
              - Frozen: 4.0 kg CO2/unit/year
              - Climate-Controlled: 1.0 kg CO2/unit/year
            
            ---
            
            ### Configuring Carbon Settings Per SKU
            
            **Each SKU can have unique carbon settings!**
            
            #### How to Configure:
            1. Go to your SKU tab (e.g., "📦 RED BRICK")
            2. Find "🌱 Carbon Footprint Settings" section (collapsed by default)
            3. Expand it and configure:
            
            **Transport Configuration:**
            - **Factory → DC Mode:** Choose Truck/Train/Ship/Air
            - **Factory → DC Distance:** Enter distance in km
            - **DC → Store Mode:** Choose Truck/Train/Ship/Air
            - **DC → Store Distance:** Enter distance in km
            
            **Product Details:**
            - **Product Weight:** Weight per unit in kg
            - **Storage Type:** Choose storage requirements
            
            #### Real-World Examples:
            
            **Construction Materials (Heavy, Domestic):**
            ```
            RED BRICK:
            - Factory→DC: Truck (300 km) - Heavy, short distance
            - DC→Store: Truck (50 km) - Local delivery
            - Weight: 25 kg/unit
            - Storage: Ambient
            Result: HIGH transport emissions (truck mode)
            ```
            
            **Imported Bulk Goods (Long Distance):**
            ```
            OPC CEMENT:
            - Factory→DC: Ship (5,000 km) - Overseas import
            - DC→Store: Train (500 km) - Bulk rail transport
            - Weight: 50 kg/unit
            - Storage: Ambient
            Result: LOWER emissions per ton-km (ship + train)
            ```
            
            **Light Products (Regional):**
            ```
            FIBER CEMENT BOARD:
            - Factory→DC: Train (1,000 km) - Regional supplier
            - DC→Store: Truck (200 km) - Last mile
            - Weight: 15 kg/unit
            - Storage: Ambient
            Result: MODERATE emissions (mixed modes)
            ```
            
            ---
            
            ### Understanding Carbon Metrics
            
            #### Individual SKU Metrics:
            
            **Total CO2 (kg):**
            - Total carbon emissions for simulation period
            - Includes transport + warehouse
            - Example: 98,930 kg CO2
            
            **CO2 per Unit (kg):**
            - Carbon footprint per product unit
            - Useful for product-level comparisons
            - Example: 0.18 kg CO2/unit
            
            **Carbon Intensity (kg/$):**
            - CO2 emissions per dollar of revenue
            - Key metric for efficiency
            - Lower is better!
            - Example: 0.0012 kg/$
            
            **Performance Rating:**
            - ⭐⭐⭐ **Excellent:** < 0.05 kg/$ (Green supply chain)
            - ⭐⭐ **Good:** 0.05-0.10 kg/$ (Above average)
            - ⭐ **Fair:** 0.10-0.15 kg/$ (Room for improvement)
            - ❌ **Poor:** > 0.15 kg/$ (Needs optimization)
            
            #### Portfolio Metrics:
            
            **Portfolio Total CO2:**
            - Total emissions across all analyzed SKUs
            - Tracks your overall carbon footprint
            
            **Avg CO2/Unit:**
            - Average carbon per unit across portfolio
            - Identifies high-emission products
            
            **Transport %:**
            - Percentage of emissions from transport
            - Typically 85-95% for most products
            - High % suggests transport optimization opportunity
            
            ---
            
            ### Carbon Optimization Strategies
            
            #### 🚛 Transport Mode Optimization:
            
            **Switch from Truck to Train:**
            - Savings: ~65% reduction (62 → 22 g/ton-km)
            - Best for: Bulk goods, non-urgent, rail-accessible
            - Example: Cement, construction materials
            
            **Switch from Truck to Ship:**
            - Savings: ~84% reduction (62 → 10 g/ton-km)
            - Best for: International, large volumes, long distances
            - Example: Imported goods, containerized cargo
            
            **Avoid Air Freight:**
            - Cost: 8x higher than truck (500 vs 62 g/ton-km)
            - Use only for: Emergencies, perishables, high-value urgent
            
            #### 📦 Warehouse Optimization:
            
            **Reduce Inventory Levels:**
            - Lower average inventory = less warehouse emissions
            - Use just-in-time when feasible
            - Balance service level vs carrying cost
            
            **Optimize Storage Type:**
            - Ambient whenever possible (lowest emissions)
            - Minimize frozen storage (8x higher than ambient)
            - Use efficient climate control
            
            #### 🎯 Green Logistics Best Practices:
            
            **1. Consolidate Shipments:**
            - Fewer trips = lower emissions
            - Full truckloads vs partial loads
            - Combine multiple SKUs
            
            **2. Optimize Routes:**
            - Shorter distances = lower emissions
            - Consider regional sourcing
            - Multi-modal optimization
            
            **3. Balance Trade-offs:**
            - Fast (air) vs Green (ship/train)
            - Cost vs Carbon
            - Service level vs Sustainability
            
            ---
            
            ### Using Carbon Data for Decision-Making
            
            #### ESG Reporting:
            - Export carbon data from Portfolio Dashboard
            - Include in sustainability reports
            - Track Scope 3 emissions (transport + warehouse)
            - Demonstrate net-zero progress
            
            #### Regulatory Compliance:
            - EU Carbon Border Adjustment Mechanism (CBAM)
            - SEC Climate Disclosure requirements
            - Supply chain emissions reporting
            - Carbon intensity tracking
            
            #### Customer Reporting:
            - Provide carbon data to customers
            - Support green procurement initiatives
            - Enable carbon-conscious sourcing
            - Differentiate with sustainability metrics
            
            #### Strategic Planning:
            - Set carbon reduction targets
            - Monitor portfolio carbon performance
            - Identify high-emission SKUs for action
            - Balance profit with planet
            
            ---
            
            ### Carbon Settings Tips
            
            #### ✅ Setting Realistic Values:
            - **Distances:** Use actual route distances (Google Maps)
            - **Weights:** Use actual product weights (from specs)
            - **Modes:** Use actual transport methods (not ideal)
            - **Storage:** Use actual warehouse conditions
            
            #### ✅ Per-SKU Configuration Benefits:
            - **Accuracy:** Different SKUs have different supply chains
            - **Optimization:** Compare scenarios per product
            - **Realism:** Mixed portfolios with varied modes
            - **Insights:** Identify which products drive emissions
            
            #### ✅ Portfolio Analysis:
            - Compare carbon across SKUs
            - Identify optimization opportunities
            - Track transport mode mix
            - Monitor carbon intensity trends
            
            #### ⚠️ Common Mistakes:
            - ❌ Using same settings for all SKUs (not realistic!)
            - ❌ Forgetting to set product weight
            - ❌ Estimating distances (use actual data)
            - ❌ Ignoring storage type (can be significant)
            
            ---
            
            ### Carbon Analytics in Portfolio Dashboard
            
            **What You'll See:**
            
            **1. Portfolio Carbon Metrics:**
            - Total CO2, Avg CO2/Unit, Carbon Intensity
            - Transport %, Portfolio Rating
            
            **2. Carbon Footprint by SKU Table:**
            - Shows: Total CO2, CO2/Unit, Carbon Intensity
            - Shows: Transport Mode, Storage Type
            - Shows: Transport CO2, Warehouse CO2, Rating
            - Sortable and filterable
            
            **3. Carbon Analytics Charts:**
            - **Bar Chart:** Total CO2 by SKU (color-coded by rating)
            - **Pie Chart:** Portfolio breakdown (Transport vs Warehouse)
            
            **4. Export with Carbon Data:**
            - CSV/Excel downloads include carbon metrics
            - Ready for ESG reports and analysis
            """)
        
        # Best Practices
        with st.expander("💡 Tips & Best Practices"):
            st.markdown("""
            ### Getting the Most Out of AI Supply Chain Twin
            
            #### 📊 Data Quality
            - ✅ **Clean data**: Remove duplicates, fix missing values
            - ✅ **Sufficient history**: 3+ months of demand data
            - ✅ **Consistent units**: Same unit of measure throughout
            - ✅ **Representative**: Data reflects normal operations
            
            #### 🎯 Starting Your Analysis
            - ✅ **Start small**: 2-3 SKUs first, then expand
            - ✅ **Use ABC**: Focus on high-value items first
            - ✅ **Test scenarios**: Try conservative estimates initially
            - ✅ **Iterate**: Refine parameters based on results
            
            #### ⚙️ Parameter Selection
            - ✅ **Use actuals**: Real costs, real lead times
            - ✅ **Be realistic**: Don't over-optimize initially
            - ✅ **Start conservative**: Higher safety stocks to start
            - ✅ **Test sensitivity**: Change one parameter at a time
            
            #### 📈 Interpreting Results
            - ✅ **Check distribution**: Look at profit variation (± value)
            - ✅ **Monitor service**: Should meet/exceed target
            - ✅ **Review charts**: Visual patterns reveal insights
            - ✅ **Compare scenarios**: Baseline vs disruption
            
            #### 🚀 Taking Action
            - ✅ **Document findings**: Note what parameters work
            - ✅ **Test before implementing**: Validate in real world
            - ✅ **Monitor actual**: Compare predictions to reality
            - ✅ **Refine model**: Update as you learn
            
            #### ⚠️ Common Mistakes to Avoid
            - ❌ **Setting unit cost too high**: Check against actual prices
            - ❌ **Unrealistic margins**: Use market-based margins
            - ❌ **Too few iterations**: Use 50+ for stable results
            - ❌ **Ignoring risk score**: High scores need attention
            - ❌ **Over-optimizing**: Leave buffer for uncertainty
            """)
        
        # Troubleshooting
        with st.expander("🔧 Troubleshooting Common Issues"):
            st.markdown("""
            ### Common Problems & Solutions
            
            #### ❌ "Average Profit is Negative"
            **Problem**: Losing money in simulation
            
            **Check:**
            - ✅ Unit cost vs selling price (margin should be positive)
            - ✅ Safety stock not too high (excessive holding costs)
            - ✅ Stockout penalty not unrealistic
            - ✅ Transport costs reasonable
            
            **Fix**: Reduce unit cost OR increase margin percentage
            
            ---
            
            #### ❌ "Service Level Below Target"
            **Problem**: Too many stockouts
            
            **Check:**
            - ✅ Safety stock sufficient for demand variability
            - ✅ Lead time accurate
            - ✅ Reorder point above safety stock
            
            **Fix**: Increase safety stock by 20-50%
            
            ---
            
            #### ❌ "Inventory Turns Too Low"
            **Problem**: Capital tied up in inventory
            
            **Check:**
            - ✅ Safety stock not excessive
            - ✅ Order quantities not too large
            - ✅ Demand forecast accurate
            
            **Fix**: Reduce safety stock gradually while monitoring service
            
            ---
            
            #### ❌ "High Risk Score"
            **Problem**: System flagging as risky
            
            **Check:**
            - ✅ Service level (biggest factor - 50% of score)
            - ✅ Profit volatility (high variation = risky)
            - ✅ Stockout frequency
            
            **Fix**: Address root cause (usually service level)
            
            ---
            
            #### ❌ "Results Don't Make Sense"
            **Problem**: Numbers seem wrong
            
            **Check:**
            - ✅ Data uploaded correctly (check column mapping)
            - ✅ Units consistent (all in same UOM)
            - ✅ Decimal points correct ($100 not $10000)
            - ✅ Sufficient historical data
            
            **Fix**: Re-upload data, verify column selection
            """)
        
        # Contact & Support
        with st.expander("📞 Support & Commercial Licensing"):
            st.markdown("""
            ### Need Help or Want to Use Commercially?
            
            #### 🎓 Educational/Personal Use
            This tool is **free for educational and personal use**.
            
            If you encounter issues:
            - Check this User Guide
            - Review the troubleshooting section above
            - Verify your data format and parameters
            
            #### 💼 Commercial Use
            For business/commercial use, you need a license.
            
            **Available Options:**
            - 🏢 **Enterprise License**: Internal company use
            - 🌐 **SaaS License**: Offer to your customers
            - 🎨 **White-Label**: Rebrand as your own
            - 🔧 **Custom Development**: Tailored features
            
            **Contact:**
            - 📧 Email: waleed.amaged80@gmail.com
            - 💼 LinkedIn: www.linkedin.com/in/waleed-abdel-mageed-cscp-pmp®-b283b316
            
            #### 🏆 About the Developer
            **Waleed A. Mageed**
            - CSCP (Certified Supply Chain Professional)
            - PMP (Project Management Professional)
            - Supply Chain & Procurement Professional
            
            ---
            
            **© 2026 Waleed A. Mageed. All Rights Reserved.**
            
            *This software is proprietary. See LICENSE for complete terms.*
            """)
        
        # Quick Reference
        st.divider()
        st.subheader("📋 Quick Reference Card")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **⚙️ Recommended Settings**
            - Iterations: 50-70
            - Horizon: 90 days
            - Service Target: 95%
            - Holding Rate: 20-25%
            """)
        
        with col2:
            st.markdown("""
            **📊 Good Benchmarks**
            - Service Level: >95%
            - Inventory Turns: 5-15x
            - Risk Score: <30
            - Lost Sales: <1% demand
            """)
        
        with col3:
            st.markdown("""
            **🎯 Success Indicators**
            - Positive profit ✅
            - Low variation (±) ✅
            - Service at/above target ✅
            - Green risk status ✅
            """)
    
    with tab_portfolio:
        st.header("🌐 Multi-SKU Portfolio Overview")
        
        # Check if data has been uploaded
        if not data_uploaded:
            st.info("📤 Please upload your data in the sidebar to view portfolio analysis.")
            st.markdown("""
            **This dashboard will show:**
            - Total portfolio revenue and profit
            - Average service level across all SKUs
            - Portfolio risk assessment
            - SKU performance comparison charts
            
            **Upload your CSV file to get started!** 👆
            """)
        else:
            # Check if we have results - look in both sku_results AND individual memory
            # Build analyzed_skus from BOTH sources to ensure we get ALL simulations
            analyzed_skus = {}
            
            # First, add from sku_results (main storage)
            for sku, result in st.session_state.get('sku_results', {}).items():
                if sku in selected_items:
                    analyzed_skus[sku] = result
            
            # Then, add any missing from individual memory states
            for item in selected_items:
                mem_key = f"memory_{item}"
                if mem_key in st.session_state:
                    mem = st.session_state[mem_key]
                    if mem.get("executed") and mem.get("results"):
                        if item not in analyzed_skus:  # Only if not already in analyzed_skus
                            analyzed_skus[item] = mem["results"]
                            # Also update sku_results for next time
                            st.session_state['sku_results'][item] = mem["results"]
            
            if not analyzed_skus:
                st.info("👉 Run simulations for individual SKUs in their respective tabs to see portfolio metrics here.")
            else:
                # Portfolio metrics
                st.subheader("📈 Portfolio Performance Metrics")
                st.caption(f"✅ Calculated from {len(analyzed_skus)} ANALYZED SKUs only (NOT including unanalyzed SKUs)")
                
                col1, col2, col3, col4 = st.columns(4)
                
                total_revenue = sum(r['sim_df']['revenue'].mean() for r in analyzed_skus.values())
                total_profit = sum(r['sim_df']['profit'].mean() for r in analyzed_skus.values())
                avg_service = np.mean([r['sim_df']['service_level'].mean() for r in analyzed_skus.values()])
            
                with col1:
                    st.metric("Total Portfolio Revenue", f"${total_revenue:,.0f}")
                with col2:
                    st.metric("Total Portfolio Profit", f"${total_profit:,.0f}")
                with col3:
                    service_delta = avg_service - target_service
                    st.metric(
                        "Avg Portfolio Service",
                        f"{avg_service:.1f}%",
                        delta=f"{service_delta:+.1f}%",
                        delta_color="normal" if service_delta >= 0 else "inverse"
                    )
                with col4:
                    st.metric("SKUs Analyzed", f"{len(analyzed_skus)}/{len(selected_items)}")
                
                # Portfolio risk heatmap
                st.subheader("🎯 Portfolio Risk Assessment")
                
                portfolio_analyzer = PortfolioAnalyzer()
                portfolio_health, critical_skus, medium_skus, healthy_skus = portfolio_analyzer.portfolio_risk_assessment(analyzed_skus)
                
                risk_col1, risk_col2, risk_col3 = st.columns(3)
                
                with risk_col1:
                    st.markdown(f"<div class='sku-card'><h4 style='color: #dc3545;'>🔴 Critical Risk</h4><p style='font-size: 2rem;'>{len(critical_skus)}</p></div>", unsafe_allow_html=True)
                    if critical_skus:
                        st.write(", ".join(critical_skus))
                
                with risk_col2:
                    st.markdown(f"<div class='sku-card'><h4 style='color: #ffc107;'>🟡 Medium Risk</h4><p style='font-size: 2rem;'>{len(medium_skus)}</p></div>", unsafe_allow_html=True)
                    if medium_skus:
                        st.write(", ".join(medium_skus))
                
                with risk_col3:
                    st.markdown(f"<div class='sku-card'><h4 style='color: #28a745;'>🟢 Healthy</h4><p style='font-size: 2rem;'>{len(healthy_skus)}</p></div>", unsafe_allow_html=True)
                    if healthy_skus:
                        st.write(", ".join(healthy_skus))
                
                # SKU comparison chart
                st.subheader("📊 SKU Performance Comparison")
                
                comparison_data = []
                for sku, result in analyzed_skus.items():
                    comparison_data.append({
                        'SKU': sku,
                        'Profit': result['sim_df']['profit'].mean(),
                        'Service Level': result['sim_df']['service_level'].mean(),
                        'Risk Score': result['analysis']['risk_analysis']['total_risk'],
                        'Inventory Turns': result['sim_df']['inventory_turns'].mean()
                    })
                
                comparison_df = pd.DataFrame(comparison_data)
                
                # ⬇️⬇️⬇️ ADDITION 2: SKU PERFORMANCE COMPARISON TABLE ⬇️⬇️⬇️
                st.subheader("SKU Performance Comparison")
                
                # Add Risk Level from actual analysis (use same classification as Portfolio Risk Assessment)
                risk_levels = []
                for sku in comparison_df['SKU']:
                    if sku in analyzed_skus:
                        # Get actual risk level from analysis
                        actual_risk = analyzed_skus[sku]['analysis']['risk_analysis']['risk_level']
                        # Map to display format (Critical/Medium/Low → Critical/Medium/Healthy)
                        if actual_risk == 'Low':
                            risk_levels.append('Healthy')
                        else:
                            risk_levels.append(actual_risk)
                    else:
                        risk_levels.append('Unknown')
                
                comparison_df['Risk Level'] = risk_levels
                
                # Display comparison table
                st.dataframe(comparison_df[['SKU', 'Profit', 'Service Level', 'Inventory Turns', 'Risk Level']], 
                           use_container_width=True)
                
                st.markdown("---")
                # ⬆️⬆️⬆️ END ADDITION 2 ⬆️⬆️⬆️
                
                # ⬇️⬇️⬇️ ADDITION 3: PORTFOLIO ANALYTICS VISUALIZATIONS ⬇️⬇️⬇️
                st.subheader("Portfolio Analytics")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Profit Contribution by SKU
                    fig_profit = px.bar(
                        comparison_df, 
                        x='SKU', 
                        y='Profit',
                        color='Risk Level',
                        color_discrete_map={
                            'Critical': '#dc3545',   # Red
                            'Caution': '#ffc107',    # Yellow
                            'Stable': '#28a745'      # Green
                        },
                        title='Profit Contribution by SKU',
                        labels={'Profit': 'Profit ($)'}
                    )
                    fig_profit.update_layout(showlegend=True)
                    st.plotly_chart(fig_profit, use_container_width=True, key="profit_chart_v2")
                
                with col2:
                    # Service Level vs Inventory Efficiency
                    # Handle negative profits by using absolute value for size
                    comparison_df_plot = comparison_df.copy()
                    comparison_df_plot['Abs_Profit'] = comparison_df_plot['Profit'].abs()
                    
                    fig_scatter = px.scatter(
                        comparison_df_plot, 
                        x='Service Level', 
                        y='Inventory Turns',
                        size='Abs_Profit',  # Use absolute value for marker size
                        color='Risk Level',
                        color_discrete_map={
                            'Critical': '#dc3545',
                            'Caution': '#ffc107',
                            'Stable': '#28a745'
                        },
                        title='Service Level vs Inventory Efficiency',
                        labels={
                            'Service Level': 'Service Level (%)', 
                            'Inventory Turns': 'Inventory Turns (ratio)'
                        },
                        hover_data=['SKU', 'Profit']
                    )
                    fig_scatter.update_layout(showlegend=True)
                    st.plotly_chart(fig_scatter, use_container_width=True, key="scatter_chart_v2")
                
                st.markdown("---")
                # ⬆️⬆️⬆️ END ADDITION 3 ⬆️⬆️⬆️
                
                # Multi-metric comparison
                fig_comparison = make_subplots(
                    rows=2, cols=2,
                    subplot_titles=('Profit by SKU', 'Service Level by SKU', 'Risk Score by SKU', 'Inventory Turns by SKU'),
                    vertical_spacing=0.15
                )
                
                fig_comparison.add_trace(
                    go.Bar(x=comparison_df['SKU'], y=comparison_df['Profit'], name='Profit', marker_color='#1f77b4'),
                    row=1, col=1
                )
                
                fig_comparison.add_trace(
                    go.Bar(x=comparison_df['SKU'], y=comparison_df['Service Level'], name='Service Level', marker_color='#2ca02c'),
                    row=1, col=2
                )
                
                # Color-code risk scores
                risk_colors = ['#dc3545' if r > 60 else '#ffc107' if r > 30 else '#28a745' for r in comparison_df['Risk Score']]
                fig_comparison.add_trace(
                    go.Bar(x=comparison_df['SKU'], y=comparison_df['Risk Score'], name='Risk Score', marker_color=risk_colors),
                    row=2, col=1
                )
                
                fig_comparison.add_trace(
                    go.Bar(x=comparison_df['SKU'], y=comparison_df['Inventory Turns'], name='Inventory Turns', marker_color='#ff7f0e'),
                    row=2, col=2
                )
                
                fig_comparison.update_yaxes(title_text="Profit ($)", row=1, col=1)
                fig_comparison.update_yaxes(title_text="Service Level (%)", row=1, col=2)
                fig_comparison.update_yaxes(title_text="Risk Score", row=2, col=1)
                fig_comparison.update_yaxes(title_text="Turns (x)", row=2, col=2)
                
                fig_comparison.update_layout(height=600, showlegend=False)
                st.plotly_chart(fig_comparison, use_container_width=True, key="portfolio_comparison_chart")
                
                # Portfolio-level recommendations
                st.subheader("💡 Portfolio-Level Strategic Recommendations")
                
                if critical_skus:
                    st.markdown(f"""
                    <div class='recommendation-critical'>
                    <strong>🚨 CRITICAL PRIORITY:</strong> {len(critical_skus)} SKU(s) require immediate intervention<br>
                    <strong>Action:</strong> Focus resources on: {', '.join(critical_skus[:3])}{'...' if len(critical_skus) > 3 else ''}<br>
                    <strong>Impact:</strong> Prevent cascading portfolio failure
                    </div>
                    """, unsafe_allow_html=True)
                
                if avg_service < target_service:
                    st.markdown(f"""
                    <div class='recommendation-high'>
                    <strong>⚠️ Portfolio Service Gap:</strong> {target_service - avg_service:.1f}% below target<br>
                    <strong>Action:</strong> Implement tiered safety stock strategy (higher for Class A SKUs)<br>
                    <strong>Impact:</strong> Bring portfolio to target service level
                    </div>
                    """, unsafe_allow_html=True)
                
                # ABC-based inventory optimization suggestion
                sku_metrics = {sku: {'revenue': result['sim_df']['revenue'].mean()} for sku, result in analyzed_skus.items()}
                abc_classes = portfolio_analyzer.classify_abc(sku_metrics)
                
                class_a_count = sum(1 for c in abc_classes.values() if c['class'] == 'A')
                if class_a_count > 0:
                    st.markdown(f"""
                    <div class='recommendation'>
                    <strong>💰 ABC Optimization Opportunity:</strong><br>
                    <strong>Analysis:</strong> {class_a_count} Class A SKU(s) drive 70% of revenue<br>
                    <strong>Action:</strong> Prioritize safety stock investment in Class A items<br>
                    <strong>Impact:</strong> Maximum ROI on working capital deployment
                    </div>
                    """, unsafe_allow_html=True)
                
                # ===== PORTFOLIO CARBON FOOTPRINT SUMMARY =====
                st.markdown("---")
                st.subheader("🌱 Portfolio Carbon Footprint Summary")
                
                # Check if carbon metrics are available
                if 'carbon_metrics' in st.session_state and st.session_state['carbon_metrics']:
                    # Filter carbon data to only include currently analyzed SKUs
                    all_carbon_data = st.session_state['carbon_metrics']
                    carbon_data = {sku: data for sku, data in all_carbon_data.items() if sku in analyzed_skus}
                    
                    if not carbon_data:
                        st.info("📊 Run simulations for individual SKUs to see carbon footprint data.")
                    else:
                        # Calculate portfolio totals
                        portfolio_total_co2 = sum(sku['total_co2'] for sku in carbon_data.values())
                        portfolio_transport_co2 = sum(sku['transport_co2'] for sku in carbon_data.values())
                        portfolio_warehouse_co2 = sum(sku['warehouse_co2'] for sku in carbon_data.values())
                        
                        # Calculate averages
                        avg_co2_per_unit = np.mean([sku['co2_per_unit'] for sku in carbon_data.values()])
                        avg_carbon_intensity = np.mean([sku['carbon_intensity'] for sku in carbon_data.values()])
                        
                        # Get portfolio rating
                        rating_text, stars, rating_color = CarbonFootprintCalculator.get_carbon_rating(avg_carbon_intensity)
                        
                        # Display portfolio metrics
                        pcol1, pcol2, pcol3, pcol4, pcol5 = st.columns(5)
                        
                        with pcol1:
                            st.metric(
                                "Portfolio Total CO2",
                                f"{portfolio_total_co2:,.0f} kg",
                                help="Total carbon emissions across all SKUs"
                            )
                        
                        with pcol2:
                            st.metric(
                                "Avg CO2/Unit",
                                f"{avg_co2_per_unit:.2f} kg",
                                help="Average carbon per unit across portfolio"
                            )
                        
                        with pcol3:
                            st.metric(
                                "Avg Carbon Intensity",
                                f"{avg_carbon_intensity:.4f} kg/$",
                                help="Average CO2 per revenue dollar"
                            )
                        
                        with pcol4:
                            transport_pct_portfolio = (portfolio_transport_co2 / portfolio_total_co2 * 100) if portfolio_total_co2 > 0 else 0
                            st.metric(
                                "Transport %",
                                f"{transport_pct_portfolio:.1f}%",
                                help="Percentage from transportation"
                            )
                        
                        with pcol5:
                            st.markdown(f"""
                            <div style='text-align: center; padding: 10px;'>
                                <h3 style='color: {rating_color}; margin: 0;'>{rating_text} {stars}</h3>
                                <p style='font-size: 12px; margin: 0;'>Portfolio Rating</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # SKU-level carbon comparison
                        st.markdown("**Carbon Footprint by SKU:**")
                        
                        carbon_comparison = []
                        for sku_name, metrics in carbon_data.items():
                            # Build transport mode string
                            transport_mode_str = f"{metrics.get('transport_mode_factory', 'N/A')} → {metrics.get('transport_mode_dc', 'N/A')}"
                            
                            carbon_comparison.append({
                                'SKU': sku_name,
                                'Total CO2 (kg)': f"{metrics['total_co2']:,.0f}",
                                'CO2/Unit (kg)': f"{metrics['co2_per_unit']:.2f}",
                                'Carbon Intensity (kg/$)': f"{metrics['carbon_intensity']:.4f}",
                                'Transport Mode': transport_mode_str,
                                'Storage': metrics.get('storage_type', 'N/A'),
                                'Transport CO2 (kg)': f"{metrics['transport_co2']:,.0f}",
                                'Warehouse CO2 (kg)': f"{metrics['warehouse_co2']:,.0f}",
                                'Rating': metrics['rating']
                            })
                        
                        carbon_df = pd.DataFrame(carbon_comparison)
                        st.dataframe(carbon_df, use_container_width=True, hide_index=True)
                        
                        # Visualizations
                        st.markdown("**Carbon Analytics:**")
                        
                        vis_col1, vis_col2 = st.columns(2)
                        
                        with vis_col1:
                            # CO2 by SKU - need numeric values for chart
                            carbon_chart_data = []
                            for sku_name, metrics in carbon_data.items():
                                carbon_chart_data.append({
                                    'SKU': sku_name,
                                    'Total CO2 (kg)': metrics['total_co2'],
                                    'Rating': metrics['rating']
                                })
                            carbon_chart_df = pd.DataFrame(carbon_chart_data)
                            
                            fig_co2_sku = px.bar(
                                carbon_chart_df,
                                x='SKU',
                                y='Total CO2 (kg)',
                                title='Total CO2 Emissions by SKU',
                                color='Rating',
                                color_discrete_map={
                                    'Excellent': '#28a745',
                                    'Good': '#2ECC71',
                                    'Fair': '#F39C12',
                                    'Poor': '#E74C3C'
                                }
                            )
                            st.plotly_chart(fig_co2_sku, use_container_width=True, key="portfolio_co2_bar")
                        
                        with vis_col2:
                            # Portfolio breakdown
                            portfolio_breakdown = pd.DataFrame({
                                'Source': ['Transport', 'Warehouse'],
                                'CO2 (kg)': [portfolio_transport_co2, portfolio_warehouse_co2]
                            })
                            
                            fig_portfolio_pie = px.pie(
                                portfolio_breakdown,
                                values='CO2 (kg)',
                                names='Source',
                                title='Portfolio Carbon Breakdown',
                                color_discrete_sequence=['#E67E22', '#9B59B6']
                            )
                            st.plotly_chart(fig_portfolio_pie, use_container_width=True, key="portfolio_carbon_pie")
                    
                else:
                    st.info("📊 Run simulations for individual SKUs to see portfolio carbon footprint summary.")
                
                # ⬇️⬇️⬇️ EXPORT RESULTS - AT END OF PORTFOLIO DASHBOARD ⬇️⬇️⬇️
                st.markdown("---")
                st.markdown("### 📥 Export Results")
                
                export_col1, export_col2 = st.columns(2)
                
                with export_col1:
                    # Export to CSV
                    csv = comparison_df.to_csv(index=False)
                    st.download_button(
                        label="📄 Download as CSV",
                        data=csv,
                        file_name=f"portfolio_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        help="Download portfolio comparison table as CSV file"
                    )
                
                with export_col2:
                    # Export to Excel
                    from io import BytesIO
                    buffer = BytesIO()
                    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                        comparison_df.to_excel(writer, sheet_name='Portfolio Comparison', index=False)
                    
                    st.download_button(
                        label="📊 Download as Excel",
                        data=buffer.getvalue(),
                        file_name=f"portfolio_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        help="Download portfolio comparison table as Excel file"
                    )
                # ⬆️⬆️⬆️ END EXPORT FEATURE ⬆️⬆️⬆️
    
    # ============================================================
    # TAB 2+: INDIVIDUAL SKU ANALYSIS
    # ============================================================
    # Only process SKU tabs if data is uploaded and SKUs are selected
    if data_uploaded and selected_items:
        for tab_idx, item in enumerate(selected_items):
            with tab_skus[tab_idx]:
                # Initialize memory for this SKU
                if f"memory_{item}" not in st.session_state:
                    st.session_state[f"memory_{item}"] = {"executed": False, "results": None}
                
                st.header(f"📦 SKU Analysis: {item}")
                
                # Extract item-specific data
                item_data = df[df[item_col] == item]
                
                if item_data.empty:
                    st.warning(f"⚠️ No data found for SKU: {item}")
                    continue
                
                # Clean and validate demand data
                raw_demand = pd.to_numeric(
                    item_data[sales_col].astype(str).str.replace(',', '').str.strip(),
                    errors='coerce'
                ).dropna()
                
                # Remove zeros and negative values
                raw_demand = raw_demand[raw_demand > 0]
                
                if raw_demand.empty:
                    st.error(f"❌ No valid positive demand data found for {item}. Please check your data.")
                    st.info(f"💡 Tip: Make sure the '{sales_col}' column contains numeric values > 0 for this SKU.")
                    continue
                
                if len(raw_demand) < 2:
                    st.warning(f"⚠️ Only {len(raw_demand)} valid data point for {item}. Need at least 2 records for statistical analysis.")
                    if len(raw_demand) == 1:
                        st.info(f"Using single data point: {raw_demand.iloc[0]:.0f} units")
                    continue
                
                mean_demand = raw_demand.mean()
                std_demand = raw_demand.std()
                
                # Validate data quality
                if pd.isna(mean_demand) or mean_demand <= 0:
                    st.error(f"⚠️ Invalid demand data for {item}: No valid positive demand values found. Skipping this SKU.")
                    continue
                
                if pd.isna(std_demand) or std_demand < 0:
                    std_demand = mean_demand * 0.2  # Assume 20% variability if std is missing
                    st.warning(f"⚠️ Could not calculate std deviation for {item}. Using estimated value: {std_demand:.0f}")
                
                if len(raw_demand) < 2:
                    st.warning(f"⚠️ Only {len(raw_demand)} data point(s) for {item}. Need at least 2 for reliable analysis.")
                    std_demand = mean_demand * 0.2  # Default assumption
                
                # Always show configuration (users can adjust and re-run anytime)
                st.info(f"📊 Historical Demand: μ={mean_demand:.0f}, σ={std_demand:.0f} (based on {len(raw_demand)} records)")
                
                # ⬇️⬇️⬇️ ADDITION 1: HISTORICAL DEMAND ANALYSIS ⬇️⬇️⬇️
                st.subheader("📊 Historical Demand Analysis")
                
                # Calculate CV
                cv = (std_demand / mean_demand * 100) if mean_demand > 0 else 0
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Mean Daily Demand", f"{mean_demand:,.0f} units")
                
                with col2:
                    st.metric("Std Deviation", f"{std_demand:,.0f} units")
                
                with col3:
                    st.metric("Coefficient of Variation", f"{cv:.1f}%")
                
                st.markdown("---")
                # ⬆️⬆️⬆️ END ADDITION 1 ⬆️⬆️⬆️
                    
                    # Sanity check for extremely high values
                if mean_demand > 1_000_000:
                    st.error(f"⚠️ WARNING: Average demand ({mean_demand:,.0f}) seems unrealistically high! Check your data or click Reset button below.")
                
                # Add reset button to clear cached values
                if st.button(f"🔄 Reset to Calculated Defaults", key=f"reset_{item}"):
                    # Force recalculation by clearing session state for this SKU
                    for key in list(st.session_state.keys()):
                        if item in key:
                            del st.session_state[key]
                    st.rerun()
                
                # Configuration section
                st.subheader("⚙️ Inventory Policy Configuration")
                
                config_col1, config_col2 = st.columns(2)
                
                with config_col1:
                    st.markdown("**Inventory Parameters**")
                    
                    # Single total lead time input
                    lead_time = st.number_input(
                        "Lead Time (days)",
                        value=10,
                        min_value=1,
                        max_value=90,
                        step=1,
                        key=f"lead_time_{item}",
                        help="Total days from order placement to delivery"
                    )
                    
                    # Smart defaults using formulas with USER'S lead time
                    z_score_95 = 1.65
                    recommended_ss = int(z_score_95 * std_demand * np.sqrt(lead_time))
                    
                    # Calculate sensible default values
                    default_ss = max(int(mean_demand * 5), recommended_ss)
                    default_qty = int(mean_demand * 10)
                    default_rop = int(mean_demand * (lead_time * 0.5))  # Half of lead time for ROP
                    
                    # Add validation to prevent unrealistic values
                    max_reasonable_ss = int(mean_demand * 100)  # Max 100 days of demand
                    max_reasonable_qty = int(mean_demand * 50)  # Max 50 days per order
                    max_reasonable_rop = int(mean_demand * 20)  # Max 20 days for reorder
                    
                    safety_stock = st.number_input(
                        "Safety Stock (units)",
                        value=min(default_ss, max_reasonable_ss),
                        min_value=0,
                        max_value=max_reasonable_ss,
                        step=500,
                        key=f"ss_{item}",
                        help=f"Recommended (95% service, {lead_time}-day LT): {recommended_ss:,}. Max: {max_reasonable_ss:,}"
                    )
                    
                    order_qty = st.number_input(
                        "Order Quantity (units)",
                        value=min(default_qty, max_reasonable_qty),
                        min_value=1,
                        max_value=max_reasonable_qty,
                        step=500,
                        key=f"qty_{item}",
                        help=f"Typical: 10-15 days of demand. Max allowed: {max_reasonable_qty:,}"
                    )
                    
                    reorder_point = st.number_input(
                        "Local Reorder Point",
                        value=min(default_rop, max_reasonable_rop),
                        min_value=0,
                        max_value=max_reasonable_rop,
                        step=100,
                        key=f"rop_{item}",
                        help=f"Trigger replenishment when below this level. Max allowed: {max_reasonable_rop:,}"
                    )
                
                with config_col2:
                    st.markdown("**Cost & Pricing**")
                    
                    # Unit cost - allow decimals below $1
                    unit_cost = st.number_input(
                        "Unit Cost ($)",
                        value=100.0,
                        min_value=0.01,
                        step=1.0,
                        format="%.2f",
                        key=f"unit_cost_{item}",
                        help="What you pay your supplier per unit (can be less than $1)"
                    )
                    
                    # Margin as percentage
                    margin_pct = st.number_input(
                        "Profit Margin (%)",
                        value=50.0,
                        min_value=0.0,
                        max_value=1000.0,
                        step=5.0,
                        format="%.1f",
                        key=f"margin_pct_{item}",
                        help="Profit margin as % of unit cost. Selling price = unit cost × (1 + margin %)"
                    )
                    
                    # Calculate margin in dollars
                    margin = unit_cost * (margin_pct / 100)
                    selling_price = unit_cost + margin
                    
                    st.caption(f"💰 Selling Price: ${selling_price:.2f}/unit (Cost: ${unit_cost:.2f} + Margin: ${margin:.2f})")
                    
                    # Advanced cost parameters
                    with st.expander("⚙️ Additional Cost Settings"):
                        holding_rate = st.slider(
                            "Annual Holding Cost Rate (%)",
                            min_value=10,
                            max_value=50,
                            value=25,
                            step=5,
                            key=f"holding_{item}",
                            help="Cost of holding inventory as % of unit cost per year"
                        )
                        
                        stockout_penalty = st.number_input(
                            "Stockout Penalty ($)",
                            value=200.0,
                            min_value=0.0,
                            step=25.0,
                            format="%.2f",
                            key=f"penalty_{item}",
                            help="Cost of losing one sale (lost profit + customer dissatisfaction)"
                        )
                        
                        transport_cost = st.number_input(
                            "Transport Cost ($/unit)",
                            value=2.0,
                            min_value=0.0,
                            step=0.5,
                            format="%.2f",
                            key=f"transport_{item}",
                            help="Cost to ship one unit between locations"
                        )
                
                # Scenario Planning moved to new section
                st.markdown("**Scenario Planning**")
                
                scenario = st.text_area(
                    "Describe Disruption Scenario:",
                    value="Normal operations",
                    height=100,
                    key=f"scenario_{item}",
                    help="Examples: 'Demand surge 20%', 'Supplier delay 7 days', 'Port strike 40% capacity loss'"
                )
                
                # Show example scenarios
                with st.expander("💡 Example Scenarios"):
                    st.markdown("""
                    - *Demand surge 25% for 2 weeks*
                    - *Factory delay 10 days*
                    - *Port strike in Shanghai 7 day delay 40% capacity reduction*
                    - *Volatile demand due to competitor stockout*
                    - *Critical emergency requiring immediate shipment*
                    """)
                
                # ===== CARBON FOOTPRINT SETTINGS (PER-SKU) =====
                with st.expander("🌱 Carbon Footprint Settings", expanded=False):
                    st.markdown("**Configure carbon tracking for this SKU**")
                    st.caption("Set unique transport modes, distances, and storage for accurate emissions tracking")
                    
                    carbon_col1, carbon_col2 = st.columns(2)
                    
                    with carbon_col1:
                        st.markdown("**🚛 Transport: Factory → DC**")
                        transport_mode_factory = st.selectbox(
                            "Transport Mode",
                            ["Truck", "Train", "Ship", "Air"],
                            index=0,
                            key=f"carbon_factory_{item}",
                            help="Primary transport from factory/supplier to distribution center"
                        )
                        distance_factory_dc = st.number_input(
                            "Distance (km)",
                            min_value=0,
                            value=500,
                            step=50,
                            key=f"carbon_dist_factory_{item}",
                            help="Distance from factory/supplier to DC"
                        )
                    
                    with carbon_col2:
                        st.markdown("**🏪 Transport: DC → Store**")
                        transport_mode_dc = st.selectbox(
                            "Transport Mode",
                            ["Truck", "Train", "Ship", "Air"],
                            index=0,
                            key=f"carbon_dc_{item}",
                            help="Last-mile transport from DC to retail/customer"
                        )
                        distance_dc_store = st.number_input(
                            "Distance (km)",
                            min_value=0,
                            value=200,
                            step=25,
                            key=f"carbon_dist_dc_{item}",
                            help="Distance from DC to store/customer"
                        )
                    
                    carbon_col3, carbon_col4 = st.columns(2)
                    
                    with carbon_col3:
                        product_weight = st.number_input(
                            "📦 Product Weight (kg/unit)",
                            min_value=0.01,
                            value=1.0,
                            step=0.1,
                            format="%.2f",
                            key=f"carbon_weight_{item}",
                            help="Weight per unit for transport emissions calculation"
                        )
                    
                    with carbon_col4:
                        storage_type = st.selectbox(
                            "🏭 Storage Type",
                            ["Ambient", "Refrigerated", "Frozen", "Climate-Controlled"],
                            index=0,
                            key=f"carbon_storage_{item}",
                            help="Warehouse storage requirements affect energy emissions"
                        )
                    
                    # Show emission factors for reference
                    with st.expander("ℹ️ Emission Factors Reference"):
                        st.markdown("""
                        **Transport (g CO2 per ton-km):**
                        - Truck: 62 (DEFRA 2023)
                        - Train: 22 (DEFRA 2023)
                        - Ship: 10 (IMO 2023)
                        - Air: 500 (IATA 2023)
                        
                        **Warehouse (kg CO2 per unit per year):**
                        - Ambient: 0.5
                        - Refrigerated: 2.0
                        - Frozen: 4.0
                        - Climate-Controlled: 1.0
                        """)
                    
                    st.info("💡 Carbon emissions will be calculated after simulation based on these settings")
                    
                    # Store carbon config for this SKU
                    st.session_state[f"carbon_config_{item}"] = {
                        'transport_mode_factory': transport_mode_factory,
                        'distance_factory_dc': distance_factory_dc,
                        'transport_mode_dc': transport_mode_dc,
                        'distance_dc_store': distance_dc_store,
                        'product_weight': product_weight,
                        'storage_type': storage_type
                    }
                
                # Execute simulation button
                if st.button(f"🚀 Execute AI Twin Simulation", key=f"exec_{item}", type="primary", use_container_width=True):
                    
                    try:
                        with st.spinner("🧠 Parsing scenario and running simulation..."):
                            # Parse scenario
                            parser = ScenarioParser()
                            disruption_profile = parser.parse(scenario)
                            
                            # Configure simulation
                            config = {
                                'mean_demand': mean_demand,
                                'std_demand': std_demand,
                                'safety_stock': safety_stock,
                                'order_qty': order_qty,
                                'reorder_point_local': reorder_point,
                                'unit_cost': unit_cost,
                                'margin': margin,
                                'penalty': stockout_penalty,
                                'holding_rate': holding_rate,
                                'transport_cost': transport_cost,
                                'lead_time': lead_time
                            }
                            
                            # Run simulation
                            twin = SupplyChainTwin(config)
                            sim_df, daily_traces = twin.simulate_scenario(
                                disruption_profile,
                                sim_days=sim_days,
                                iterations=iterations
                            )
                            
                            # AI decision analysis
                            decision_engine = DecisionEngine()
                            analysis = decision_engine.analyze_performance(
                                sim_df,
                                baseline_profit=None,
                                target_service=target_service,
                                mean_demand=mean_demand
                            )
                            
                            # Store results
                            st.session_state[f"memory_{item}"]["executed"] = True
                            st.session_state[f"memory_{item}"]["results"] = {
                                'disruption_profile': disruption_profile,
                                'sim_df': sim_df,
                                'daily_traces': daily_traces,
                                'analysis': analysis,
                                'config': config,
                                'scenario': scenario  # Store scenario text for reports
                            }
                            
                            # Store in global portfolio results
                            st.session_state['sku_results'][item] = st.session_state[f"memory_{item}"]["results"]
                            
                            # Calculate and store carbon metrics IMMEDIATELY after simulation
                            try:
                                # Get per-SKU carbon configuration
                                carbon_config = st.session_state.get(f"carbon_config_{item}", {
                                    'transport_mode_factory': 'Truck',
                                    'distance_factory_dc': 500,
                                    'transport_mode_dc': 'Truck',
                                    'distance_dc_store': 200,
                                    'product_weight': 1.0,
                                    'storage_type': 'Ambient'
                                })
                                
                                sim_results_for_carbon = sim_df
                                avg_service_level_carbon = sim_results_for_carbon['service_level'].mean()
                                avg_lost_sales_carbon = sim_results_for_carbon['lost_sales'].mean()
                                avg_revenue_carbon = sim_results_for_carbon['revenue'].mean()
                                avg_inventory_carbon = sim_results_for_carbon['avg_inventory'].mean()
                                
                                # Calculate fulfilled units
                                if avg_service_level_carbon < 100:
                                    estimated_total_demand = avg_lost_sales_carbon / (1 - avg_service_level_carbon/100) if avg_service_level_carbon < 99.9 else avg_lost_sales_carbon * 100
                                else:
                                    estimated_total_demand = avg_lost_sales_carbon * 100
                                total_units_carbon = estimated_total_demand - avg_lost_sales_carbon
                                if total_units_carbon <= 0:
                                    total_units_carbon = avg_revenue_carbon / 100
                                
                                # Transport emissions using per-SKU settings
                                transport_co2_factory = CarbonFootprintCalculator.calculate_transport_co2(
                                    carbon_config['distance_factory_dc'], 
                                    carbon_config['product_weight'], 
                                    total_units_carbon, 
                                    carbon_config['transport_mode_factory']
                                )
                                transport_co2_dc = CarbonFootprintCalculator.calculate_transport_co2(
                                    carbon_config['distance_dc_store'], 
                                    carbon_config['product_weight'], 
                                    total_units_carbon, 
                                    carbon_config['transport_mode_dc']
                                )
                                total_transport_co2 = transport_co2_factory + transport_co2_dc
                                
                                # Warehouse emissions using per-SKU settings
                                warehouse_co2 = CarbonFootprintCalculator.calculate_warehouse_co2(
                                    avg_inventory_carbon, 
                                    sim_days, 
                                    carbon_config['storage_type']
                                )
                                
                                # Total carbon
                                total_co2 = total_transport_co2 + warehouse_co2
                                carbon_intensity = total_co2 / avg_revenue_carbon if avg_revenue_carbon > 0 else 0
                                co2_per_unit = total_co2 / total_units_carbon if total_units_carbon > 0 else 0
                                rating_text, _, _ = CarbonFootprintCalculator.get_carbon_rating(carbon_intensity)
                                
                                # Store carbon metrics WITH transport mode info
                                if 'carbon_metrics' not in st.session_state:
                                    st.session_state['carbon_metrics'] = {}
                                st.session_state['carbon_metrics'][item] = {
                                    'total_co2': total_co2,
                                    'co2_per_unit': co2_per_unit,
                                    'carbon_intensity': carbon_intensity,
                                    'transport_co2': total_transport_co2,
                                    'warehouse_co2': warehouse_co2,
                                    'rating': rating_text,
                                    'transport_mode_factory': carbon_config['transport_mode_factory'],
                                    'transport_mode_dc': carbon_config['transport_mode_dc'],
                                    'storage_type': carbon_config['storage_type']
                                }
                            except:
                                pass  # If carbon calculation fails, just skip it
                        
                        st.success("✅ Simulation complete!")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error during simulation: {str(e)}")
                        st.error("Please check your configuration and try again.")
                        with st.expander("🔍 Technical Details"):
                            st.code(f"{type(e).__name__}: {str(e)}")
                            import traceback
                        st.code(traceback.format_exc())
                
                # Display results if available
                mem = st.session_state[f"memory_{item}"]
                
                if mem["executed"] and mem["results"]:
                    try:
                        results = mem["results"]
                        disruption_profile = results.get('disruption_profile', {})
                        sim_df = results.get('sim_df', pd.DataFrame())
                        daily_traces = results.get('daily_traces', {})
                        analysis = results.get('analysis', {})
                        scenario = results.get('scenario', 'Normal operations')  # Retrieve scenario for reports
                        
                        # Validate that we have the necessary data
                        if sim_df.empty or not analysis:
                            st.warning("⚠️ Incomplete simulation results. Please re-run the simulation.")
                            st.session_state[f"memory_{item}"]["executed"] = False
                            st.stop()
                        
                        # Add prominent reconfigure button at top
                        
                        st.divider()
                        
                        # --- PARSED SCENARIO ---
                        with st.expander("📋 Parsed Disruption Profile", expanded=True):  # Changed to expanded=True so users see it
                            profile_col1, profile_col2, profile_col3, profile_col4 = st.columns(4)
                            with profile_col1:
                                st.metric("Demand Shift", f"{disruption_profile.get('demand_shift', 0):+}%")
                            with profile_col2:
                                st.metric("Lead Time Impact", f"+{disruption_profile.get('lead_time_shift', 0)} days")
                            with profile_col3:
                                st.metric("Supplier Reliability", f"{disruption_profile.get('supplier_reliability', 100)}%")
                            with profile_col4:
                                # Get urgency from TWO sources and show the highest priority
                                parsed_urgency = disruption_profile.get('urgency', 'Normal')
                                risk_level = analysis.get('risk_analysis', {}).get('risk_level', 'Low')
                                
                                # Map risk_level to urgency (Critical > Medium > Low/Normal)
                                risk_urgency_map = {
                                    'Critical': 'Critical',
                                    'Medium': 'Medium',
                                    'Low': 'Normal'
                                }
                                risk_urgency = risk_urgency_map.get(risk_level, 'Normal')
                                
                                # Take the HIGHER urgency (Critical > Medium > Normal)
                                urgency_priority = {'Critical': 3, 'Medium': 2, 'Normal': 1}
                                if urgency_priority.get(risk_urgency, 1) > urgency_priority.get(parsed_urgency, 1):
                                    final_urgency = risk_urgency
                                    urgency_source = "(Risk-Based)"
                                else:
                                    final_urgency = parsed_urgency
                                    urgency_source = "(Keyword-Based)"
                                
                                urgency_class = {
                                    'Critical': 'critical-status',
                                    'Medium': 'medium-status',
                                    'Normal': 'healthy-status'
                                }.get(final_urgency, 'medium-status')
                                
                                st.markdown(f"<div class='{urgency_class}'>Urgency: {final_urgency}</div>", unsafe_allow_html=True)
                                st.caption(f"Source: {urgency_source}")
                            
                            # Debug info (can be removed after testing)
                            if st.checkbox("Show Debug Info", key=f"debug_{item}"):
                                st.code(f"Scenario text: {scenario}")
                                st.code(f"Parsed urgency: {parsed_urgency}")
                                st.code(f"Risk-based urgency: {risk_urgency} (from risk_level={risk_level})")
                                st.code(f"Final urgency: {final_urgency}")
                                st.code(f"Full parsed profile: {json.dumps(disruption_profile, indent=2)}")
                        
                        # --- EXECUTIVE DIRECTIVE ---
                        st.subheader("🎯 Executive Strategic Directive")
                        
                        # Create decision engine instance
                        decision_engine = DecisionEngine()
                        directive = decision_engine.generate_executive_directive(analysis, disruption_profile)
                        
                        status_class = {
                            '🔴 CRITICAL': 'critical-status',
                            '🟡 CAUTION': 'medium-status',
                            '🟢 STABLE': 'healthy-status'
                        }[directive['status']]
                        
                        st.markdown(f"""
                        <div class='sku-card'>
                        <div class='{status_class}'>{directive['status']}</div>
                        <h3>{directive['directive']}</h3>
                        <p><strong>Primary Action:</strong> {directive['primary_action']}</p>
                        <p><strong>Timeline:</strong> {directive['timeline']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # --- PERFORMANCE METRICS ---
                        st.subheader(f"📊 Performance Metrics for {item}")
                        st.caption(f"⚠️ These metrics are for THIS SKU ONLY, not the whole portfolio")
                        
                        avg_profit = sim_df['profit'].mean()
                        avg_service = sim_df['service_level'].mean()
                        profit_std = sim_df['profit'].std()
                        avg_turns = sim_df['inventory_turns'].mean()
                        avg_lost_sales = sim_df['lost_sales'].mean()
                        
                        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
                        
                        with metric_col1:
                            st.metric("Average Profit", f"${avg_profit:,.0f}", delta=f"±${profit_std:,.0f}")
                        with metric_col2:
                            service_delta = avg_service - target_service
                            st.metric(
                                "Service Level",
                                f"{avg_service:.1f}%",
                                delta=f"{service_delta:+.1f}%",
                                delta_color="normal" if service_delta >= 0 else "inverse"
                            )
                        with metric_col3:
                            st.metric("Inventory Turns", f"{avg_turns:.1f}x")
                        with metric_col4:
                            st.metric("Avg Lost Sales", f"{avg_lost_sales:,.0f} units")
                        
                        # Risk score with breakdown
                        risk_analysis = analysis['risk_analysis']
                        st.metric(
                            "🎯 Overall Risk Score",
                            f"{risk_analysis['total_risk']:.0f}/100",
                            help=f"Service Gap: {risk_analysis['components']['service_gap']:.0f} | Volatility: {risk_analysis['components']['profit_volatility']:.0f} | Stockout: {risk_analysis['components']['stockout_cost']:.0f}"
                        )
                        
                        # ===== CARBON FOOTPRINT METRICS =====
                        st.markdown("---")
                        st.subheader("🌱 Carbon Footprint Analysis")
                        
                        try:
                            # Get per-SKU carbon configuration
                            carbon_config = st.session_state.get(f"carbon_config_{item}", {
                                'transport_mode_factory': 'Truck',
                                'distance_factory_dc': 500,
                                'transport_mode_dc': 'Truck',
                                'distance_dc_store': 200,
                                'product_weight': 1.0,
                                'storage_type': 'Ambient'
                            })
                            
                            # Validate required columns exist
                            required_cols = ['lost_sales', 'avg_inventory', 'revenue', 'service_level']
                            missing_cols = [col for col in required_cols if col not in sim_df.columns]
                            
                            if missing_cols:
                                st.warning(f"⚠️ Carbon calculation unavailable. Missing data: {', '.join(missing_cols)}")
                            else:
                                # Calculate total fulfilled units from service level
                                avg_revenue_carbon = sim_df['revenue'].mean()
                                avg_service_level = sim_df['service_level'].mean()
                                avg_lost_sales = sim_df['lost_sales'].mean()
                                
                                # Estimate total demand and fulfilled units
                                if avg_service_level < 100:
                                    estimated_total_demand = avg_lost_sales / (1 - avg_service_level/100) if avg_service_level < 99.9 else avg_lost_sales * 100
                                else:
                                    estimated_total_demand = avg_lost_sales * 100
                                
                                total_units = estimated_total_demand - avg_lost_sales
                                
                                # Ensure positive value
                                if total_units <= 0:
                                    total_units = avg_revenue_carbon / 100
                                
                                avg_inventory_carbon = sim_df['avg_inventory'].mean()
                                simulation_days_carbon = sim_days
                                
                                # Transport emissions using per-SKU settings
                                transport_co2_factory = CarbonFootprintCalculator.calculate_transport_co2(
                                    carbon_config['distance_factory_dc'],
                                    carbon_config['product_weight'],
                                    total_units,
                                    carbon_config['transport_mode_factory']
                                )
                                
                                transport_co2_dc = CarbonFootprintCalculator.calculate_transport_co2(
                                    carbon_config['distance_dc_store'],
                                    carbon_config['product_weight'],
                                    total_units,
                                    carbon_config['transport_mode_dc']
                                )
                                
                                total_transport_co2 = transport_co2_factory + transport_co2_dc
                                
                                # Warehouse emissions using per-SKU settings
                                warehouse_co2 = CarbonFootprintCalculator.calculate_warehouse_co2(
                                    avg_inventory_carbon,
                                    simulation_days_carbon,
                                    carbon_config['storage_type']
                                )
                                
                                # Total carbon footprint
                                total_co2 = total_transport_co2 + warehouse_co2
                                
                                # Carbon intensity (CO2 per dollar)
                                avg_revenue_carbon = sim_df['revenue'].mean()
                                carbon_intensity = total_co2 / avg_revenue_carbon if avg_revenue_carbon > 0 else 0
                                
                                # CO2 per unit
                                co2_per_unit = total_co2 / total_units if total_units > 0 else 0
                                
                                # Get rating
                                rating_text, stars, rating_color = CarbonFootprintCalculator.get_carbon_rating(carbon_intensity)
                                
                                # Display metrics
                                carbon_col1, carbon_col2, carbon_col3, carbon_col4 = st.columns(4)
                                
                                with carbon_col1:
                                    st.metric(
                                        "Total CO2",
                                        f"{total_co2:,.0f} kg",
                                        help="Total carbon emissions for simulation period"
                                    )
                                
                                with carbon_col2:
                                    st.metric(
                                        "CO2 per Unit",
                                        f"{co2_per_unit:.2f} kg",
                                        help="Carbon footprint per product unit"
                                    )
                                
                                with carbon_col3:
                                    st.metric(
                                        "Carbon Intensity",
                                        f"{carbon_intensity:.4f} kg/$",
                                        help="CO2 emissions per dollar of revenue"
                                    )
                                
                                with carbon_col4:
                                    st.markdown(f"""
                                    <div style='text-align: center; padding: 10px;'>
                                        <h3 style='color: {rating_color}; margin: 0;'>{rating_text} {stars}</h3>
                                        <p style='font-size: 12px; margin: 0;'>Carbon Rating</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                
                                # Carbon breakdown
                                st.markdown("**Carbon Emissions Breakdown:**")
                                
                                breakdown_col1, breakdown_col2 = st.columns(2)
                                
                                with breakdown_col1:
                                    transport_pct = (total_transport_co2 / total_co2 * 100) if total_co2 > 0 else 0
                                    warehouse_pct = (warehouse_co2 / total_co2 * 100) if total_co2 > 0 else 0
                                    
                                    breakdown_data = pd.DataFrame({
                                        'Source': ['Transport', 'Warehouse'],
                                        'CO2 (kg)': [total_transport_co2, warehouse_co2],
                                        'Percentage': [f"{transport_pct:.1f}%", f"{warehouse_pct:.1f}%"]
                                    })
                                    
                                    st.dataframe(breakdown_data, use_container_width=True, hide_index=True)
                                
                                with breakdown_col2:
                                    fig_carbon = px.pie(
                                        breakdown_data,
                                        values='CO2 (kg)',
                                        names='Source',
                                        title='Carbon Emissions by Source',
                                        color_discrete_sequence=['#E67E22', '#9B59B6']
                                    )
                                    fig_carbon.update_traces(textposition='inside', textinfo='percent+label')
                                    st.plotly_chart(fig_carbon, use_container_width=True, key=f"carbon_pie_{item}")
                                
                                # Show current carbon configuration
                                st.caption(f"🌱 **Configuration:** Factory→DC: {carbon_config['transport_mode_factory']} ({carbon_config['distance_factory_dc']}km) | DC→Store: {carbon_config['transport_mode_dc']} ({carbon_config['distance_dc_store']}km) | Weight: {carbon_config['product_weight']}kg | Storage: {carbon_config['storage_type']}")
                                
                                # Store carbon metrics for portfolio summary
                                if 'carbon_metrics' not in st.session_state:
                                    st.session_state['carbon_metrics'] = {}
                                
                                st.session_state['carbon_metrics'][item] = {
                                    'total_co2': total_co2,
                                    'co2_per_unit': co2_per_unit,
                                    'carbon_intensity': carbon_intensity,
                                    'transport_co2': total_transport_co2,
                                    'warehouse_co2': warehouse_co2,
                                    'rating': rating_text,
                                    'transport_mode_factory': carbon_config['transport_mode_factory'],
                                    'transport_mode_dc': carbon_config['transport_mode_dc'],
                                    'storage_type': carbon_config['storage_type']
                                }
                        
                        except Exception as e:
                            st.error(f"⚠️ Error calculating carbon footprint: {str(e)}")
                            st.info("💡 Please ensure the simulation completed successfully and try again.")
                        
                        # --- VISUALIZATIONS ---
                        st.subheader("📈 Performance Analytics")
                    
                        # Profit distribution
                        fig_profit = go.Figure()
                        fig_profit.add_trace(go.Histogram(
                        x=sim_df['profit'],
                        nbinsx=30,
                        name='Profit Distribution',
                        marker_color='#1f77b4'
                        ))
                        fig_profit.add_vline(
                        x=avg_profit,
                        line_dash="dash",
                        line_color="red",
                        annotation_text=f"Mean: ${avg_profit:,.0f}"
                        )
                        fig_profit.update_layout(
                        title="Profit Distribution (Monte Carlo)",
                        xaxis_title="Net Profit ($)",
                        yaxis_title="Frequency",
                        height=300
                        )
                        st.plotly_chart(fig_profit, use_container_width=True, key=f"profit_chart_{item}")
                        
                        # Inventory dynamics
                        fig_inv = go.Figure()
                        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
                        
                        for i, (iter_name, trace_data) in enumerate(daily_traces.items()):
                            if trace_data:
                                days = [d['day'] for d in trace_data]
                                local_inv = [d['local'] for d in trace_data]
                                fig_inv.add_trace(go.Scatter(
                                    x=days,
                                    y=local_inv,
                                    mode='lines',
                                    name=f'Simulation {i+1}',
                                    line=dict(color=colors[i], width=1.5),
                                    opacity=0.7
                                ))
                        
                        fig_inv.add_hrect(
                        y0=0, y1=mean_demand * 2,
                        fillcolor="red", opacity=0.1,
                        annotation_text="High Stockout Risk Zone",
                        annotation_position="top left"
                        )
                        
                        fig_inv.update_layout(
                        title="Inventory Dynamics - Local DC (Sample Paths)",
                        xaxis_title="Day",
                        yaxis_title="Inventory Level (units)",
                        height=400,
                        hovermode='x unified'
                        )
                        st.plotly_chart(fig_inv, use_container_width=True, key=f"inventory_chart_{item}")
                        
                        # Service level box plot
                        fig_service = go.Figure()
                        fig_service.add_trace(go.Box(
                        y=sim_df['service_level'],
                        name='Service Level',
                        marker_color='#2ca02c',
                        boxmean='sd'
                        ))
                        fig_service.add_hline(
                        y=target_service,
                        line_dash="dash",
                        line_color="red",
                        annotation_text=f"Target: {target_service}%"
                        )
                        fig_service.update_layout(
                        title="Service Level Variability",
                        yaxis_title="Service Level (%)",
                        height=300
                        )
                        st.plotly_chart(fig_service, use_container_width=True, key=f"service_chart_{item}")
                        
                        # --- AI INSIGHTS & RECOMMENDATIONS ---
                        st.subheader("💡 AI-Generated Insights & Recommendations")
                        
                        if analysis['insights']:
                            st.markdown("**Key Insights:**")
                            for insight in analysis['insights']:
                                st.markdown(f"<div class='insight-box'>{insight}</div>", unsafe_allow_html=True)
                        
                        if analysis['recommendations']:
                            st.markdown("**Recommended Actions:**")
                            for rec in analysis['recommendations']:
                                rec_class = {
                                'Critical': 'recommendation-critical',
                                'High': 'recommendation-high',
                                'Medium': 'recommendation',
                                'Low': 'recommendation'
                            }.get(rec['priority'], 'recommendation')
                            
                            st.markdown(f"""
                            <div class='{rec_class}'>
                            <strong>[{rec['priority']} Priority] {rec['action']}</strong><br>
                            📈 <em>Impact:</em> {rec['impact']}<br>
                            💰 <em>Cost:</em> {rec['cost']}
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # --- EXPORT RESULTS ---
                        st.subheader("📥 Export Results")
                        
                        export_col1, export_col2 = st.columns(2)
                        
                        with export_col1:
                            # Summary report
                            summary_report = f"""
AI SUPPLY CHAIN TWIN - SIMULATION REPORT
SKU: {item}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

SCENARIO: {scenario}

DISRUPTION PROFILE:
- Demand Shift: {disruption_profile['demand_shift']:+}%
- Lead Time Impact: +{disruption_profile['lead_time_shift']} days
- Supplier Reliability: {disruption_profile['supplier_reliability']}%
- Urgency: {disruption_profile['urgency']}

PERFORMANCE RESULTS:
- Average Profit: ${avg_profit:,.0f} (±${profit_std:,.0f})
- Service Level: {avg_service:.1f}% (Target: {target_service}%)
- Inventory Turns: {avg_turns:.1f}x
- Risk Assessment: {risk_analysis['risk_level']} ({risk_analysis['total_risk']:.0f}/100)

EXECUTIVE DIRECTIVE:
{directive['status']}
{directive['directive']}
Primary Action: {directive['primary_action']}
Timeline: {directive['timeline']}

KEY INSIGHTS:
{chr(10).join(['- ' + insight for insight in analysis['insights']])}

RECOMMENDATIONS:
{chr(10).join(['- [' + rec['priority'] + '] ' + rec['action'] + ': ' + rec['impact'] for rec in analysis['recommendations']])}
                            """
                            
                            st.download_button(
                                label="📄 Download Summary Report",
                                data=summary_report,
                                file_name=f"ai_twin_report_{item}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                                mime="text/plain",
                                key=f"download_summary_{item}"
                            )
                        
                        with export_col2:
                            # Detailed CSV
                            csv_data = sim_df.to_csv(index=False)
                            st.download_button(
                                label="📊 Download Detailed Results (CSV)",
                                data=csv_data,
                                file_name=f"simulation_results_{item}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv",
                                key=f"download_csv_{item}"
                            )
                        
                    except Exception as e:
                        st.error(f"❌ Error displaying results: {str(e)}")
                        st.warning("The simulation results may be incomplete. Please try re-running the simulation.")
                        col_err1, col_err2 = st.columns(2)
                        with col_err1:
                            if st.button("🔄 Clear Results & Retry", key=f"clear_{item}"):
                                st.session_state[f"memory_{item}"] = {"executed": False, "results": None}
                                if item in st.session_state.get('sku_results', {}):
                                    del st.session_state['sku_results'][item]
                                st.rerun()
                        with st.expander("🔍 Technical Details (for debugging)"):
                            st.code(f"{type(e).__name__}: {str(e)}")
                            import traceback
                            st.code(traceback.format_exc())
                
                else:
                    st.info("👆 Configure your inventory policy and scenario above, then click 'Execute AI Twin Simulation'")

if __name__ == "__main__":
    main()
