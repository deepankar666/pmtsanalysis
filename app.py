from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import plotly.express as px
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Global variable to hold the dataframe and company details
df_resolved = None
df_in_progress = None

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

    df_resolved = df_resolved.merge(action_counts_resolved, on='Action Required By')

    def color_code(count):
        if count == 1:
            return 'green'
        elif count <= 3:
            return 'yellow'
        else:
            return 'red'

    df_resolved['Color'] = df_resolved['Count'].apply(color_code)

    fig_resolved = px.bar(
        df_resolved,
        x='Action Required By',
        y='Count',
        color='Color',
        color_discrete_map={'green': 'green', 'yellow': 'yellow', 'red': 'red'},
        hover_data={'Count': True, 'Ticket No.': True, 'Incident': True, 'Color': False},
        title='Action Required By Analysis - Resolved Tickets'
    )

    fig_resolved.update_layout(
        width=1200,
        height=700,
        xaxis_title='Action Required By',
        yaxis_title='Count',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        title_x=0.5
    )

    action_required_by_chart_resolved = fig_resolved.to_html(full_html=False)

    charts = {
        'action_required_by_chart_resolved': action_required_by_chart_resolved
    }

    return render_template('index_resolved.html', charts=charts, total_resolved_tickets=total_resolved_tickets)

@app.route('/index_in_progress', methods=['GET'])
def index_in_progress():
    global df_in_progress
    if df_in_progress is None:
        return redirect(url_for('home'))

    total_in_progress_tickets = len(df_in_progress)
    action_counts_in_progress = df_in_progress['Action Required By'].value_counts().reset_index()
    action_counts_in_progress.columns = ['Action Required By', 'Count']

    df_in_progress = df_in_progress.merge(action_counts_in_progress, on='Action Required By')

    def color_code(count):
        if count == 1:
            return 'green'
        elif count <= 3:
            return 'yellow'
        else:
            return 'red'

    df_in_progress['Color'] = df_in_progress['Count'].apply(color_code)

    fig_in_progress = px.bar(
        df_in_progress,
        x='Action Required By',
        y='Count',
        color='Color',
        color_discrete_map={'green': 'green', 'yellow': 'yellow', 'red': 'red'},
        hover_data={'Count': True, 'Ticket No.': True, 'Incident': True, 'Color': False},
        title='Action Required By Analysis - In Progress Tickets'
    )

    fig_in_progress.update_layout(
        width=1200,
        height=700,
        xaxis_title='Action Required By',
        yaxis_title='Count',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        title_x=0.5
    )

    action_required_by_chart_in_progress = fig_in_progress.to_html(full_html=False)

    charts = {
        'action_required_by_chart_in_progress': action_required_by_chart_in_progress
    }

    return render_template('index_in_progress.html', charts=charts, total_in_progress_tickets=total_in_progress_tickets)

if __name__ == '__main__':
    app.run(debug=True)
