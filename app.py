from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import pandas as pd
import plotly.express as px
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'supersecretkey'  # Needed for flashing messages

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Global variable to hold the dataframe and company details
df_resolved = None
df_in_progress = None

consultant_filters = [
    "Michael srujay (SAP-MM)",
    "Krishna vamsi (SAP-OTC)",
    "Aishwarya Bangari (SAP-PS & PM)",
    "Anki reddy (SAP-FICO)",
    "GBT (SAP)",
    "Vipin Tamrakar (SAP-PM)",
    "R. Srividya (SAP-ABAP)",
    "Mythreyee - (SAP-Master Data)"
]

def get_color_scale(df):
    conditions = [
        (df['Count'] == 1),
        (df['Count'] > 1) & (df['Count'] <= 3),
        (df['Count'] > 3)
    ]
    colors = ['green', 'yellow', 'red']
    return pd.cut(df['Count'], bins=[0, 1, 3, float('inf')], labels=colors, include_lowest=True)

@app.route('/', methods=['GET', 'POST'])
def home():
    global df_resolved, df_in_progress
    if request.method == 'POST':
        resolved_file = request.files.get('resolved_file')
        in_progress_file = request.files.get('in_progress_file')

        if resolved_file and resolved_file.filename != '':
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], resolved_file.filename)
            resolved_file.save(file_path)
            df_resolved = pd.read_excel(file_path, engine='openpyxl')
            df_resolved.columns = df_resolved.columns.str.strip()
            return redirect(url_for('index_resolved'))

        if in_progress_file and in_progress_file.filename != '':
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], in_progress_file.filename)
            in_progress_file.save(file_path)
            df_in_progress = pd.read_excel(file_path, engine='openpyxl')
            df_in_progress.columns = df_in_progress.columns.str.strip()
            return redirect(url_for('index_in_progress'))

    return render_template('home.html')

@app.route('/index_resolved', methods=['GET'])
def index_resolved():
    global df_resolved
    if df_resolved is None:
        return redirect(url_for('home'))

    total_resolved_tickets = len(df_resolved)
    action_counts_resolved = df_resolved['Action Required By'].value_counts().reset_index()
    action_counts_resolved.columns = ['Action Required By', 'Count']

    # Create hover data for each consultant
    df_resolved['Hover Info'] = df_resolved.apply(lambda row: f"Ticket No: {row['Ticket No.']}, Incident: {row['Incident']}", axis=1)
    hover_data_resolved = df_resolved.groupby('Action Required By').agg(
        Hover_Info=('Hover Info', lambda x: '<br>'.join(x)),
        Total_Count=('Ticket No.', 'count')
    ).reset_index()

    action_counts_resolved = action_counts_resolved.merge(hover_data_resolved, on='Action Required By', how='left')
    action_counts_resolved['Color'] = get_color_scale(action_counts_resolved)

    fig_resolved = px.bar(
        action_counts_resolved,
        x='Action Required By',
        y='Count',
        color='Color',
        title='Action Required By Analysis - Resolved Tickets',
        hover_data={'Total_Count': True, 'Hover_Info': True},
        color_discrete_map={
            'green': 'green',
            'yellow': 'yellow',
            'red': 'red'
        }
    )

    fig_resolved.update_traces(hovertemplate='%{x}<br>Total Tickets: %{customdata[0]}<br>%{customdata[1]}<extra></extra>')
    fig_resolved.update_layout(
        width=1200,
        height=700,
        xaxis_title='Action Required By',
        yaxis_title='Count',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        title_x=0.5,
        showlegend=False
    )

    action_required_by_chart_resolved = fig_resolved.to_html(full_html=False)

    return render_template('index_resolved.html', charts={'action_required_by_chart_resolved': action_required_by_chart_resolved}, total_resolved_tickets=total_resolved_tickets)

@app.route('/index_in_progress', methods=['GET'])
def index_in_progress():
    global df_in_progress
    if df_in_progress is None:
        return redirect(url_for('home'))

    total_in_progress_tickets = len(df_in_progress)
    action_counts_in_progress = df_in_progress['Action Required By'].value_counts().reset_index()
    action_counts_in_progress.columns = ['Action Required By', 'Count']

    # Create hover data for each consultant
    df_in_progress['Hover Info'] = df_in_progress.apply(lambda row: f"Ticket No: {row['Ticket No.']}, Incident: {row['Incident']}", axis=1)
    hover_data_in_progress = df_in_progress.groupby('Action Required By').agg(
        Hover_Info=('Hover Info', lambda x: '<br>'.join(x)),
        Total_Count=('Ticket No.', 'count')
    ).reset_index()

    action_counts_in_progress = action_counts_in_progress.merge(hover_data_in_progress, on='Action Required By', how='left')
    action_counts_in_progress['Color'] = get_color_scale(action_counts_in_progress)

    fig_in_progress = px.bar(
        action_counts_in_progress,
        x='Action Required By',
        y='Count',
        color='Color',
        title='Action Required By Analysis - In Progress Tickets',
        hover_data={'Total_Count': True, 'Hover_Info': True},
        color_discrete_map={
            'green': 'green',
            'yellow': 'yellow',
            'red': 'red'
        }
    )

    fig_in_progress.update_traces(hovertemplate='%{x}<br>Total Tickets: %{customdata[0]}<br>%{customdata[1]}<extra></extra>')
    fig_in_progress.update_layout(
        width=1200,
        height=700,
        xaxis_title='Action Required By',
        yaxis_title='Count',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        title_x=0.5,
        showlegend=False
    )

    action_required_by_chart_in_progress = fig_in_progress.to_html(full_html=False)

    return render_template('index_in_progress.html', charts={'action_required_by_chart_in_progress': action_required_by_chart_in_progress}, total_in_progress_tickets=total_in_progress_tickets)

@app.route('/get_filtered_data', methods=['POST'])
def get_filtered_data():
    global df_resolved, df_in_progress
    data_type = request.json['data_type']

    if data_type == 'resolved':
        df = df_resolved
    else:
        df = df_in_progress

    if df is None or 'Action Required By' not in df.columns:
        return jsonify({'error': 'Data not available or column not found'}), 400

    df_filtered = df[df['Action Required By'].isin(consultant_filters)]

    action_counts = df_filtered['Action Required By'].value_counts().reset_index()
    action_counts.columns = ['Action Required By', 'Count']

    # Create hover data for each consultant
    df_filtered['Hover Info'] = df_filtered.apply(lambda row: f"Ticket No: {row['Ticket No.']}, Incident: {row['Incident']}", axis=1)
    hover_data_filtered = df_filtered.groupby('Action Required By').agg(
        Hover_Info=('Hover Info', lambda x: '<br>'.join(x)),
        Total_Count=('Ticket No.', 'count')
    ).reset_index()

    action_counts = action_counts.merge(hover_data_filtered, on='Action Required By', how='left')
    action_counts['Color'] = get_color_scale(action_counts)

    fig = px.bar(
        action_counts,
        x='Action Required By',
        y='Count',
        color='Color',
        title='Action Required By Analysis - SAP Consultants',
        hover_data={'Total_Count': True, 'Hover_Info': True},
        color_discrete_map={
            'green': 'green',
            'yellow': 'yellow',
            'red': 'red'
        }
    )

    fig.update_traces(hovertemplate='%{x}<br>Total Tickets: %{customdata[0]}<br>%{customdata[1]}<extra></extra>')
    fig.update_layout(
        width=1200,
        height=700,
        xaxis_title='Action Required By',
        yaxis_title='Count',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        title_x=0.5,
        showlegend=False
    )

    chart_html = fig.to_html(full_html=False)

    return jsonify({'chart': chart_html})

if __name__ == '__main__':
    app.run(debug=True)
