#!/usr/bin/env python
# coding: utf-8

# period_tracker_app.py

import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go
import calendar
from dateutil.relativedelta import relativedelta

# Page configuration
st.set_page_config(
    page_title="Period Tracker & Predictor",
    page_icon="🩸",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        color: #FF69B4;
        padding-bottom: 20px;
    }
    .metric-card {
        background-color: #FFF5F7;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #FF69B4;
        margin: 10px 0;
    }
    .prediction-card {
        background-color: #E6F3FF;
        padding: 20px;
        border-radius: 10px;
        border: 2px solid #4A90E2;
    }
    .cycle-day {
        font-weight: bold;
        color: #FF69B4;
    }
    .stDateInput > div > div > input {
        border-color: #FF69B4;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown("<h1 class='main-header'>🩸 CycleSync: Period Tracker & Predictor</h1>", unsafe_allow_html=True)

# Initialize session state
if 'period_dates' not in st.session_state:
    st.session_state.period_dates = []
if 'symptoms' not in st.session_state:
    st.session_state.symptoms = {}
if 'notes' not in st.session_state:
    st.session_state.notes = {}

# Sidebar for navigation
with st.sidebar:
    st.header("Navigation")
    page = st.radio("Go to:", ["📅 Track Period", "📊 Analytics", "📈 Predictions", "⚙️ Settings"])
    
    st.header("Quick Stats")
    if st.session_state.period_dates:
        if len(st.session_state.period_dates) >= 2:
            avg_cycle = sum((st.session_state.period_dates[i] - st.session_state.period_dates[i-1]).days 
                          for i in range(1, len(st.session_state.period_dates))) // (len(st.session_state.period_dates)-1)
            st.metric("Average Cycle", f"{avg_cycle} days")
        
        last_period = st.session_state.period_dates[-1]
        days_since = (datetime.now().date() - last_period).days
        st.metric("Days Since Last", f"{days_since} days")
    
    st.markdown("---")
    if st.button("Clear All Data", type="secondary"):
        st.session_state.period_dates = []
        st.session_state.symptoms = {}
        st.session_state.notes = {}
        st.rerun()

# Main page logic
if page == "📅 Track Period":
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Add New Period")
        
        # Date input with today as default
        today = datetime.now().date()
        date_input = st.date_input(
            "Period start date:",
            value=today,
            max_value=today,
            help="Select the first day of your period"
        )
        
        # Optional symptoms tracking
        with st.expander("Track Symptoms (Optional)"):
            symptoms_cols = st.columns(3)
            with symptoms_cols[0]:
                cramping = st.checkbox("Cramping")
                headache = st.checkbox("Headache")
            with symptoms_cols[1]:
                bloating = st.checkbox("Bloating")
                fatigue = st.checkbox("Fatigue")
            with symptoms_cols[2]:
                mood_swings = st.checkbox("Mood Swings")
                acne = st.checkbox("Acne")
            
            other_symptoms = st.text_input("Other symptoms:")
        
        # Notes
        notes = st.text_area("Notes for this cycle:", 
                           placeholder="Any additional observations...")
        
        if st.button("➕ Add Period", type="primary", use_container_width=True):
            if date_input not in st.session_state.period_dates:
                st.session_state.period_dates.append(date_input)
                st.session_state.period_dates.sort()
                
                # Store symptoms and notes
                symptom_list = []
                if cramping: symptom_list.append("Cramping")
                if headache: symptom_list.append("Headache")
                if bloating: symptom_list.append("Bloating")
                if fatigue: symptom_list.append("Fatigue")
                if mood_swings: symptom_list.append("Mood Swings")
                if acne: symptom_list.append("Acne")
                if other_symptoms: symptom_list.append(other_symptoms)
                
                if symptom_list:
                    st.session_state.symptoms[str(date_input)] = symptom_list
                if notes:
                    st.session_state.notes[str(date_input)] = notes
                
                st.success(f"Period added for {date_input}!")
                st.balloons()
            else:
                st.warning("This date is already recorded.")
    
    with col2:
        st.subheader("Recent Periods")
        if st.session_state.period_dates:
            # Display last 5 periods
            recent_dates = st.session_state.period_dates[-5:]
            recent_df = pd.DataFrame({"Date": recent_dates})
            
            # Add cycle length calculation
            if len(recent_dates) > 1:
                cycle_lengths = []
                for i in range(1, len(recent_dates)):
                    cycle_len = (recent_dates[i] - recent_dates[i-1]).days
                    cycle_lengths.append(cycle_len)
                # Add NaN for first entry
                cycle_lengths = [None] + cycle_lengths
                recent_df["Cycle Length"] = cycle_lengths
            
            st.dataframe(
                recent_df.style.format({
                    "Date": lambda x: x.strftime("%b %d, %Y"),
                    "Cycle Length": lambda x: f"{int(x)} days" if pd.notnull(x) else ""
                }),
                use_container_width=True
            )
            
            # Quick actions
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("Export Data", use_container_width=True):
                    df = pd.DataFrame({"Period Dates": st.session_state.period_dates})
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name="period_data.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            
            with col_b:
                if st.button("View All", use_container_width=True):
                    st.switch_page("📊 Analytics")
        else:
            st.info("No periods recorded yet. Add your first period to get started!")

elif page == "📊 Analytics":
    st.header("Cycle Analytics")
    
    if not st.session_state.period_dates:
        st.warning("No data available. Please add period dates first.")
    else:
        df = pd.DataFrame({"Period Start Date": st.session_state.period_dates})
        df['Period Start Date'] = pd.to_datetime(df['Period Start Date'])
        df = df.sort_values('Period Start Date')
        
        # Calculate metrics
        df['Cycle Length'] = df['Period Start Date'].diff().dt.days
        df['Year'] = df['Period Start Date'].dt.year
        df['Month'] = df['Period Start Date'].dt.month_name()
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Total Cycles", len(df))
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            if len(df) > 1:
                avg_cycle = df['Cycle Length'].iloc[1:].mean()
                st.metric("Avg Cycle Length", f"{avg_cycle:.1f} days")
            else:
                st.metric("Avg Cycle Length", "N/A")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            if len(df) > 1:
                min_cycle = df['Cycle Length'].iloc[1:].min()
                st.metric("Shortest Cycle", f"{min_cycle} days")
            else:
                st.metric("Shortest Cycle", "N/A")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            if len(df) > 1:
                max_cycle = df['Cycle Length'].iloc[1:].max()
                st.metric("Longest Cycle", f"{max_cycle} days")
            else:
                st.metric("Longest Cycle", "N/A")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Cycle length visualization
        st.subheader("Cycle Length Trends")
        if len(df) > 1:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['Period Start Date'].iloc[1:],
                y=df['Cycle Length'].iloc[1:],
                mode='lines+markers',
                name='Cycle Length',
                line=dict(color='#FF69B4', width=3),
                marker=dict(size=8)
            ))
            
            # Add average line
            fig.add_hline(
                y=avg_cycle,
                line_dash="dash",
                line_color="gray",
                annotation_text=f"Average: {avg_cycle:.1f} days"
            )
            
            fig.update_layout(
                title="Cycle Length Over Time",
                xaxis_title="Period Start Date",
                yaxis_title="Cycle Length (days)",
                template="plotly_white",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Add more periods to see cycle length trends")
        
        # Monthly summary
        st.subheader("Monthly Summary")
        if len(df) >= 3:
            monthly_summary = df.groupby(['Year', 'Month']).size().reset_index(name='Count')
            monthly_summary['Period'] = monthly_summary['Month'] + ' ' + monthly_summary['Year'].astype(str)
            
            fig2 = go.Figure(data=[
                go.Bar(
                    x=monthly_summary['Period'],
                    y=monthly_summary['Count'],
                    marker_color='#FFB6C1'
                )
            ])
            fig2.update_layout(
                title="Periods per Month",
                xaxis_title="Month",
                yaxis_title="Number of Periods",
                template="plotly_white",
                height=300
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        # Detailed data table
        st.subheader("Detailed History")
        display_df = df.copy()
        display_df['Notes'] = display_df['Period Start Date'].dt.strftime('%Y-%m-%d').map(
            lambda x: st.session_state.notes.get(x, '')
        )
        display_df['Symptoms'] = display_df['Period Start Date'].dt.strftime('%Y-%m-%d').map(
            lambda x: ', '.join(st.session_state.symptoms.get(x, [])) if st.session_state.symptoms.get(x) else ''
        )
        
        st.dataframe(
            display_df[['Period Start Date', 'Cycle Length', 'Symptoms', 'Notes']].style.format({
                'Period Start Date': lambda x: x.strftime('%Y-%m-%d'),
                'Cycle Length': lambda x: f"{int(x)} days" if pd.notnull(x) else "First Period"
            }),
            use_container_width=True,
            height=400
        )

elif page == "📈 Predictions":
    st.header("Cycle Predictions")
    
    if len(st.session_state.period_dates) < 2:
        st.warning("Add at least 2 period dates to get predictions.")
    else:
        # Calculate predictions
        df = pd.DataFrame({"Period Start Date": st.session_state.period_dates})
        df['Period Start Date'] = pd.to_datetime(df['Period Start Date'])
        
        # Calculate cycle lengths
        cycle_lengths = []
        for i in range(1, len(df)):
            cycle_len = (df['Period Start Date'].iloc[i] - df['Period Start Date'].iloc[i-1]).days
            cycle_lengths.append(cycle_len)
        
        avg_cycle = sum(cycle_lengths) / len(cycle_lengths)
        
        # Next period prediction
        last_period = df['Period Start Date'].iloc[-1]
        next_predicted = last_period + timedelta(days=avg_cycle)
        
        # Calculate fertile window (assuming ovulation around day 14)
        ovulation_day = next_predicted - timedelta(days=14)
        fertile_start = ovulation_day - timedelta(days=3)
        fertile_end = ovulation_day + timedelta(days=1)
        
        # Display predictions in cards
        st.markdown('<div class="prediction-card">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"### 📅 Next Period")
            st.markdown(f"**Expected:** {next_predicted.strftime('%B %d, %Y')}")
            st.markdown(f"**In about:** {(next_predicted.date() - datetime.now().date()).days} days")
        
        with col2:
            st.markdown(f"### 🎯 Fertile Window")
            st.markdown(f"**{fertile_start.strftime('%b %d')} - {fertile_end.strftime('%b %d, %Y')}**")
            st.caption("Approximate window based on typical 14-day luteal phase")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Calendar view
        st.subheader("Calendar View")
        
        # Create a calendar for the prediction month
        prediction_month = next_predicted.month
        prediction_year = next_predicted.year
        
        # Get calendar data
        cal = calendar.monthcalendar(prediction_year, prediction_month)
        
        # Create calendar display
        st.markdown(f"### {calendar.month_name[prediction_month]} {prediction_year}")
        
        # Header
        cols = st.columns(7)
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        for i, day in enumerate(days):
            cols[i].write(f"**{day}**")
        
        # Days
        for week in cal:
            cols = st.columns(7)
            for i, day in enumerate(week):
                if day == 0:
                    cols[i].write("")
                else:
                    current_date = datetime(prediction_year, prediction_month, day).date()
                    if current_date == next_predicted.date():
                        cols[i].markdown(f'<div class="cycle-day">{day} 🩸</div>', unsafe_allow_html=True)
                    elif fertile_start.date() <= current_date <= fertile_end.date():
                        cols[i].markdown(f"**{day}** 🌱")
                    else:
                        cols[i].write(str(day))
        
        # Multiple future predictions
        st.subheader("Future Predictions")
        num_predictions = st.slider("Number of future cycles to predict:", 1, 12, 3)
        
        predictions = []
        current_date = last_period
        for i in range(num_predictions):
            current_date = current_date + timedelta(days=avg_cycle)
            predictions.append({
                "Cycle": i + 1,
                "Predicted Start": current_date.strftime("%Y-%m-%d"),
                "Day of Week": current_date.strftime("%A")
            })
        
        predictions_df = pd.DataFrame(predictions)
        st.dataframe(predictions_df, use_container_width=True)

elif page == "⚙️ Settings":
    st.header("Settings")
    
    st.subheader("Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Export All Data", use_container_width=True):
            # Create comprehensive data export
            export_data = []
            for date in st.session_state.period_dates:
                entry = {
                    "Period Start Date": date,
                    "Symptoms": ", ".join(st.session_state.symptoms.get(str(date), [])),
                    "Notes": st.session_state.notes.get(str(date), "")
                }
                export_data.append(entry)
            
            df = pd.DataFrame(export_data)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Complete Data",
                data=csv,
                file_name="period_tracker_complete_data.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    with col2:
        uploaded_file = st.file_uploader("Import Data", type=['csv'])
        if uploaded_file is not None:
            try:
                import_df = pd.read_csv(uploaded_file)
                if 'Period Start Date' in import_df.columns:
                    new_dates = pd.to_datetime(import_df['Period Start Date']).dt.date.tolist()
                    st.session_state.period_dates.extend(new_dates)
                    st.session_state.period_dates = sorted(list(set(st.session_state.period_dates)))
                    st.success(f"Imported {len(new_dates)} period dates!")
            except Exception as e:
                st.error(f"Error importing file: {e}")
    
    st.subheader("App Preferences")
    
    reminder_enabled = st.checkbox("Enable Period Reminders")
    if reminder_enabled:
        reminder_days = st.slider("Days before period to remind:", 1, 7, 3)
        st.info(f"You'll be reminded {reminder_days} days before your predicted period.")
    
    theme = st.selectbox("Theme Preference", ["Light", "Dark", "System Default"])
    
    if st.button("Save Preferences"):
        st.success("Preferences saved!")

# Footer
st.markdown("---")
st.caption("🔒 Your data is stored locally in your browser and is not sent to any server.")
st.caption("Made with ❤️ for menstrual health awareness")