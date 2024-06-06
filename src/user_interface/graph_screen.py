from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QGridLayout, QFrame
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT

from enum import Enum

class GraphWindow(QWidget):
    def __init__(self,selected_models, x_param, y_param, parent=None):
        super().__init__(parent)
        self.selected_models = selected_models
        self.x_param = x_param
        self.y_param = y_param
        self.initUI()

    def initUI(self):
        self.setStyleSheet("background-color: #3a4556;")  # Set the background color of the window

        layout = QVBoxLayout()
        scroll_area = QScrollArea(self)  # Use a scroll area to manage multiple graphs
        scroll_widget = QWidget()  # This widget will contain all the frames
        grid_layout = QGridLayout(scroll_widget)

        # Number of columns is fixed to 3 for your case
        cols = 3
        num_models = len(self.selected_models)
        rows = (num_models + cols - 1) // cols  # Calculate required rows

        for index, model_name in enumerate(self.selected_models):
            frame = QFrame(scroll_widget)
            frame.setFrameShape(QFrame.Shape.StyledPanel)
            frame.setStyleSheet("QFrame { background-color: #2d3848; border-radius: 5px; }")  # Set the frame color
            frame_layout = QVBoxLayout()
            self.add_graph_to_frame(frame_layout, model_name, self.x_param, self.y_param)
            frame.setLayout(frame_layout)
            grid_layout.addWidget(frame, index // cols, index % cols)

        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        self.setLayout(layout)

        # Set the window height dynamically based on the number of rows
        base_height = 400  # Height for one row
        self.resize(1200, base_height * rows)  # Adjust width if necessary

        self.setWindowTitle('Graphs')

    def add_graph_to_frame(self, layout, model_name, x_param, y_param):
        if x_param == 'Money':
            if y_param == 'Games Played per Simulation':
                self.createMoneyVsGamesPlayedPerSimulation(layout, model_name)
            elif y_param == 'Win Rate':
                self.createMoneyVsWinRate(layout, model_name)
            elif y_param == 'Loss Rate':
                self.createMoneyVsLoseRate(layout, model_name)
            elif y_param == 'Total Simulations':
                self.createMoneyVsTotalSimulations(layout, model_name)

        if x_param == 'Games Played per Simulation':
            if y_param == 'Win Rate':
                self.createGamesPlayedVsWinRate(layout, model_name)
            elif y_param == 'Loss Rate':
                self.createGamesPlayedVsLoseRate(layout, model_name)
            elif y_param == 'Money':
                self.createGamesPlayedVsMoney(layout, model_name)

        if x_param == 'Total Simulations':
            if y_param == 'Win Rate':
                self.createTotalSimulationsVsWinRate(layout, model_name)
            elif y_param == 'Loss Rate':
                self.createTotalSimulationsVsLoseRate(layout, model_name)
            elif y_param == 'Money':
                self.createMoneyVsTotalSimulations(layout, model_name)
            elif y_param == 'Games Played per Simulation':
                self.createTotalSimulationsVsGamesPlayedPerSimulation(layout, model_name)

        if x_param == 'Simulation':
            if y_param == 'Average ROI':
                self.createAverageROI(layout, model_name)

# Money Graphs
    def createMoneyVsTotalSimulations(self, layout, model_name):
        file_location = FileLocations[model_name].value
        df = pd.read_excel(file_location)

        fig = Figure()
        ax = fig.add_subplot(111)

        # Group by simulation and get the last row of each group
        grouped = df.groupby('Simulation')
        last_rows = grouped.tail(1)

        # Count the number of simulations that reached each unique money value
        money_counts = last_rows['Money'].value_counts().sort_index()

        # Scatter plot of the money counts
        ax.scatter(money_counts.index, money_counts.values, alpha=0.6)

        ax.set_xlabel('Money')
        ax.set_ylabel('Number of Simulations')
        ax.set_title(f'{model_name} Money vs Number of Simulations')
        ax.grid(True)

        canvas = FigureCanvas(fig)
        toolbar = QVBoxLayout()
        toolbar.addWidget(NavigationToolbar2QT(canvas, self))

        layout.addLayout(toolbar)
        layout.addWidget(canvas)


    def createMoneyVsGamesPlayedPerSimulation(self, layout, model_name):
        file_location = FileLocations[model_name].value
        df = pd.read_excel(file_location)

        fig = Figure()
        ax = fig.add_subplot(111)

        grouped = df.groupby('Simulation')
        for simulation_number, data in grouped:
            ax.plot(data['Money'],data.index, label=f'Simulation {simulation_number}', alpha=0.6)

        ax.set_xlabel('Money')
        ax.set_ylabel('Games Played')
        ax.set_title(f'{model_name} Money vs Games Played per Simulation')
        #ax.legend(loc='upper right', bbox_to_anchor=(1.15, 1), ncol=2)  # Adjust legend position
        ax.grid(True)

        canvas = FigureCanvas(fig)
        toolbar = QVBoxLayout()
        toolbar.addWidget(NavigationToolbar2QT(canvas, self))
        layout.addLayout(toolbar)

        layout.addWidget(canvas)

    def createMoneyVsLoseRate(self, layout, model_name):
        avg_lose_rates = []
        avg_moneys = []
        simulation_names = []

        file_location = FileLocations[model_name].value
        df = pd.read_excel(file_location)

        fig = Figure()
        ax = fig.add_subplot(111)

        grouped = df.groupby('Simulation')
        for simulation_number, data in grouped:
            wins = data['Result'].str.count('Win').sum()
            ties = data['Result'].str.count('Tie').sum()
            loses = data['Result'].str.count('Lose').sum()
            total_games = wins + ties + loses
            avg_lose_rate = loses / total_games * 100 if total_games > 0 else 0

            avg_lose_rates.append(avg_lose_rate)
            avg_moneys.append(data['Money'].mean())
            simulation_names.append(f'Simulation {simulation_number}')

        ax.set_xlabel('Average Money')
        ax.set_ylabel('Average Lose Rate (%)')
        ax.set_title(f'Average Lose Rate vs Average Money for {model_name} Simulations')
        ax.grid(True)

        canvas = FigureCanvas(fig)
        toolbar = QVBoxLayout()
        toolbar.addWidget(NavigationToolbar2QT(canvas, self))
        layout.addLayout(toolbar)

        layout.addWidget(canvas)

    def createMoneyVsWinRate(self, layout, model_name):
        file_location = FileLocations[model_name].value
        df = pd.read_excel(file_location)

        fig = Figure()
        ax = fig.add_subplot(111)

        grouped = df.groupby('Simulation')
        for simulation_number, data in grouped:
            wins = data['Result'].str.count('Win').sum()
            ties = data['Result'].str.count('Tie').sum()
            loses = data['Result'].str.count('Lose').sum()
            total_games = wins + ties + loses
            avg_win_rate = wins / total_games * 100 if total_games > 0 else 0

            cmap = plt.get_cmap('RdYlGn')
            color = cmap(avg_win_rate / 100)
            ax.scatter(data['Money'].mean(), avg_win_rate, label=f'Simulation {simulation_number}', alpha=0.6, color=color)

        ax.set_xlabel('Average Money')
        ax.set_ylabel('Win Rate (%)')
        ax.set_title(f'{model_name} Average Money vs Win Rate')
        ax.grid(True)

        ax.set_ylim([0, 100])

        canvas = FigureCanvas(fig)
        toolbar = QVBoxLayout()
        toolbar.addWidget(NavigationToolbar2QT(canvas, self))
        layout.addLayout(toolbar)

        layout.addWidget(canvas)

    # Games Played per Simulation Graphs
    def createGamesPlayedVsWinRate(self, layout, model_name):
        file_location = FileLocations[model_name].value
        df = pd.read_excel(file_location)

        fig = Figure()
        ax = fig.add_subplot(111)

        # Group by simulation and calculate the total games played and win rate for each simulation
        grouped = df.groupby('Simulation')
        total_games_played = []
        avg_win_rates = []

        for simulation_number, data in grouped:
            wins = data['Result'].str.count('Win').sum()
            total_games = len(data)
            avg_win_rate = wins / total_games * 100 if total_games > 0 else 0

            total_games_played.append(total_games)
            avg_win_rates.append(avg_win_rate)

        # Create scatter plot
        scatter = ax.scatter(total_games_played, avg_win_rates, c=avg_win_rates, cmap='RdYlGn', alpha=0.6)

        ax.set_xlabel('Total Games Played')
        ax.set_ylabel('Average Win Rate (%)')
        ax.set_title(f'{model_name} Games Played vs Average Win Rate')
        ax.grid(True)

        ax.set_ylim([0, 100])

        # Adding a color bar to show the win rate intensity
        cbar = fig.colorbar(scatter, ax=ax)
        cbar.set_label('Win Rate (%)')

        canvas = FigureCanvas(fig)
        toolbar = QVBoxLayout()
        toolbar.addWidget(NavigationToolbar2QT(canvas, self))
        layout.addLayout(toolbar)

        layout.addWidget(canvas)

    def createGamesPlayedVsLoseRate(self, layout, model_name):
        avg_lose_rates = []
        total_games_played = []

        file_location = FileLocations[model_name].value
        df = pd.read_excel(file_location)

        grouped = df.groupby('Simulation')
        for simulation_number, data in grouped:
            wins = data['Result'].str.count('Win').sum()
            ties = data['Result'].str.count('Tie').sum()
            loses = data['Result'].str.count('Lose').sum()
            total_games = wins + ties + loses
            avg_lose_rate = loses / total_games * 100 if total_games > 0 else 0

            avg_lose_rates.append(avg_lose_rate)
            total_games_played.append(total_games)

        fig = Figure()
        ax = fig.add_subplot(111)

        cmap = plt.get_cmap('RdYlGn_r')
        colors = [cmap(rate / 100) for rate in avg_lose_rates]
        scatter = ax.scatter(total_games_played, avg_lose_rates, c=avg_lose_rates, cmap='RdYlGn_r', alpha=0.6)

        ax.set_xlabel('Total Games Played')
        ax.set_ylabel('Average Lose Rate (%)')
        ax.set_title(f'{model_name} Games Played vs Average Lose Rate')
        ax.grid(True)

        ax.set_ylim([0, 100])

        # Adding a color bar to show the lose rate intensity
        cbar = fig.colorbar(scatter, ax=ax)
        cbar.set_label('Lose Rate (%)')

        canvas = FigureCanvas(fig)
        toolbar = QVBoxLayout()
        toolbar.addWidget(NavigationToolbar2QT(canvas, self))
        layout.addLayout(toolbar)

        layout.addWidget(canvas)

    def createGamesPlayedVsMoney(self, layout, model_name):
        file_location = FileLocations[model_name].value
        df = pd.read_excel(file_location)

        fig = Figure()
        ax = fig.add_subplot(111)

        grouped = df.groupby('Simulation')
        for simulation_number, data in grouped:
            ax.plot(data.index, data['Money'], label=f'Simulation {simulation_number}')

        ax.set_xlabel('Games Played')
        ax.set_ylabel('Money')
        ax.set_title(f'{model_name} Games Played vs Money')
        ax.legend()
        ax.grid(True)

        canvas = FigureCanvas(fig)
        toolbar = QVBoxLayout()
        toolbar.addWidget(NavigationToolbar2QT(canvas, self))
        layout.addLayout(toolbar)

        layout.addWidget(canvas)
    # Total Simulations Graphs

    def createTotalSimulationsVsWinRate(self, layout, model_name):
        file_location = FileLocations[model_name].value
        df = pd.read_excel(file_location)

        fig = Figure()
        ax = fig.add_subplot(111)

        # Group by simulation and calculate the total games played and win rate for each simulation
        grouped = df.groupby('Simulation')
        total_simulations = len(grouped)
        avg_win_rates = []

        for simulation_number, data in grouped:
            wins = data['Result'].str.count('Win').sum()
            total_games = len(data)
            avg_win_rate = wins / total_games * 100 if total_games > 0 else 0

            avg_win_rates.append(avg_win_rate)

        # Create scatter plot
        scatter = ax.scatter(range(total_simulations), avg_win_rates, c=avg_win_rates, cmap='RdYlGn', alpha=0.6)

        ax.set_xlabel('Simulation Number')
        ax.set_ylabel('Average Win Rate (%)')
        ax.set_title(f'{model_name} Total Simulations by Win Rate')
        ax.grid(True)

        ax.set_ylim([0, 100])

        # Adding a color bar to show the win rate intensity
        cbar = fig.colorbar(scatter, ax=ax)
        cbar.set_label('Win Rate (%)')

        canvas = FigureCanvas(fig)
        toolbar = QVBoxLayout()
        toolbar.addWidget(NavigationToolbar2QT(canvas, self))
        layout.addLayout(toolbar)

        layout.addWidget(canvas)

    def createTotalSimulationsVsLoseRate(self, layout, model_name):
        file_location = FileLocations[model_name].value
        df = pd.read_excel(file_location)

        fig = Figure()
        ax = fig.add_subplot(111)

        # Group by simulation and calculate the lose rate for each simulation
        grouped = df.groupby('Simulation')
        avg_lose_rates = []

        for simulation_number, data in grouped:
            loses = data['Result'].str.count('Lose').sum()
            total_games = len(data)
            avg_lose_rate = loses / total_games * 100 if total_games > 0 else 0

            avg_lose_rates.append(avg_lose_rate)

        # Create density plot
        sns.kdeplot(avg_lose_rates, ax=ax, shade=True, color="r")

        ax.set_xlabel('Lose Rate (%)')
        ax.set_ylabel('Density')
        ax.set_title(f'{model_name} Density of Lose Rates Across Simulations')
        ax.grid(True)

        ax.set_ylim([0, 100])

        canvas = FigureCanvas(fig)
        toolbar = QVBoxLayout()
        toolbar.addWidget(NavigationToolbar2QT(canvas, self))
        layout.addLayout(toolbar)

        layout.addWidget(canvas)

    def createTotalSimulationsVsGamesPlayedPerSimulation(self, layout, model_name):
        file_location = FileLocations[model_name].value
        df = pd.read_excel(file_location)

        fig = Figure()
        ax = fig.add_subplot(111)

        # Group by simulation and calculate the total games played and games played per simulation
        grouped = df.groupby('Simulation')
        total_games_played = []
        avg_games_played_per_simulation = []

        for simulation_number, data in grouped:
            total_games = len(data)
            avg_games_played = total_games / len(grouped)
            total_games_played.append(total_games)
            avg_games_played_per_simulation.append(avg_games_played)

        # Create scatter plot
        scatter = ax.scatter(total_games_played, avg_games_played_per_simulation, c=avg_games_played_per_simulation, cmap='RdYlGn', alpha=0.6)

        ax.set_xlabel('Total Games Played')
        ax.set_ylabel('Average Games Played per Simulation')
        ax.set_title(f'{model_name} Total Games vs Average Games Played per Simulation')
        ax.grid(True)

        # Adding a color bar to show the games played intensity
        cbar = fig.colorbar(scatter, ax=ax)
        cbar.set_label('Average Games Played per Simulation')

        canvas = FigureCanvas(fig)
        toolbar = QVBoxLayout()
        toolbar.addWidget(NavigationToolbar2QT(canvas, self))
        layout.addLayout(toolbar)
        layout.addWidget(canvas)

    def createAverageROI(self, layout, model_name): # histogram
        file_location = FileLocations[model_name].value
        df = pd.read_excel(file_location)
        
        # Group by simulation and calculate average ROI
        grouped = df.groupby('Simulation')['ROI'].mean().reset_index()
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        sns.histplot(grouped['ROI'], bins=30, kde=True, ax=ax, color='blue')
        
        ax.set_xlabel('ROI (%)')
        ax.set_ylabel('Frequency')
        ax.set_title(f'ROI Histogram for {model_name} Simulations')
        ax.grid(True)
        
        canvas = FigureCanvas(fig)
        toolbar = QVBoxLayout()
        toolbar.addWidget(NavigationToolbar2QT(canvas, self))
        layout.addLayout(toolbar)
        
        layout.addWidget(canvas)

class FileLocations(Enum):
    ALWAYS_HIT = 'src/brute_force/always_hit_results/always_hit_results.xlsx'
    ALWAYS_STAND = 'src/brute_force/always_stand_results/always_stand_results.xlsx'
    RANDOM_HIT_STAND = 'src/brute_force/random_hitstand_results/random_hitstand_results.xlsx'
    BASIC_STRATEGY_WITHOUTCOUNTING = 'src/basic_strategy/basic_strategy_results/basic_strategy_results.xlsx'
    BASIC_STRATEGY_WITHCOUNTING = 'src/basic_strategy/counting_strategy_results/counting_strategy_results.xlsx'
    HISTORICAL_DATA = 'src/historical_data/historical_data_results/historical_data_results.xlsx'
    RL_MODEL = 'src/reincforment_learing/reincforment_learing_results/reincforment_learing_results.xlsx'
