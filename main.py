import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QLineEdit, QListWidget, QHBoxLayout, QStackedWidget, QProgressBar
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
from twitterbot import scrape_tweet, parse_tweet


class ScraperThread(QThread):
    scrape_complete = pyqtSignal(str)
    progress_update = pyqtSignal(int)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            self.progress_update.emit(0)
            html_content = scrape_tweet(self.url)
            tweet_data = parse_tweet(html_content)
            self.scrape_complete.emit(tweet_data)
        except Exception as e:
            self.scrape_complete.emit(f"Error: {str(e)}")
        finally:
            self.progress_update.emit(100)


class TwitterApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Twitter Bot")
        self.setGeometry(100, 100, 800, 800)
        self.setStyleSheet(self.get_stylesheet())

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        central_layout = QVBoxLayout(central_widget)

        self.button_bar = self.create_top_button_bar()
        central_layout.addWidget(self.button_bar)

        self.stacked_widget = QStackedWidget(self)
        central_layout.addWidget(self.stacked_widget)

        self.create_main_screen()
        self.create_log_screen()
        self.read_log()

    def create_top_button_bar(self):
        button_bar = QWidget(self)
        button_bar.setFixedHeight(60)

        button_layout = QHBoxLayout(button_bar)
        button_layout.setContentsMargins(20, 10, 20, 10)
        button_layout.setSpacing(20)

        home_button = QPushButton("Home")
        home_button.clicked.connect(self.show_home_screen)
        settings_button = QPushButton("Profile Scrape")
        settings_button.clicked.connect(self.show_profile_screen)
        logs_button = QPushButton("Logs")
        logs_button.clicked.connect(self.show_log_screen)
        favorites_button = QPushButton("Favorites")
        logout_button = QPushButton("Logout")

        button_layout.addWidget(home_button)
        button_layout.addWidget(settings_button)
        button_layout.addWidget(logs_button)
        button_layout.addWidget(favorites_button)
        button_layout.addWidget(logout_button)

        button_bar.setLayout(button_layout)
        button_bar.setStyleSheet("background-color: #000000;")

        return button_bar

    def create_main_screen(self):
        main_screen = QWidget()
        main_layout = QVBoxLayout(main_screen)

        title_label = QLabel("Twitter Bot")
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        search_label = QLabel("Type the URL for tweet:")
        main_layout.addWidget(search_label)
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("e.g., https://x.com/profilename/status/1870682589281009748")
        main_layout.addWidget(self.search_bar)

        recommend_button = QPushButton("Scrape!")
        recommend_button.clicked.connect(self.start_scraping)
        main_layout.addWidget(recommend_button)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)

        self.recommendation_list = QListWidget()
        main_layout.addWidget(self.recommendation_list)

        footer = QLabel('Powered by playwright')
        footer.setFont(QFont("Arial", 24, QFont.Bold))
        footer.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(footer)

        self.stacked_widget.addWidget(main_screen)

    def create_log_screen(self):
        log_screen = QWidget()
        log_layout = QVBoxLayout(log_screen)

        log_label = QLabel("Logs")
        log_label.setFont(QFont("Arial", 24, QFont.Bold))
        log_label.setAlignment(Qt.AlignCenter)
        log_layout.addWidget(log_label)

        self.log_list = QListWidget()
        log_layout.addWidget(self.log_list)

        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.read_log)
        log_layout.addWidget(refresh_button)

        self.stacked_widget.addWidget(log_screen)

    def start_scraping(self):
        url = self.search_bar.text()
        if url:
            self.recommendation_list.clear()
            self.progress_bar.setValue(0)
            self.thread = ScraperThread(url)
            self.thread.scrape_complete.connect(self.display_scraped_data)
            self.thread.progress_update.connect(self.update_progress)
            self.thread.start()

    def display_scraped_data(self, data):
        if "Error" in data:
            self.recommendation_list.addItem(data)
        else:
            self.recommendation_list.addItem(f"Tweet Data: {data}")


    def update_progress(self, progress):
        self.progress_bar.setValue(progress)

    def show_home_screen(self):
        self.stacked_widget.setCurrentIndex(0)

    def show_profile_screen(self):
        self.stacked_widget.setCurrentIndex(2)

    def show_log_screen(self):
        self.stacked_widget.setCurrentIndex(1)

    def read_log(self):
        try:
            with open('log.txt', 'r', encoding='utf-8') as file:
                self.log_list.clear()
                log_content = file.readlines()
                self.log_list.addItems([line.strip() for line in log_content])
        except FileNotFoundError:
            self.log_list.addItem("No logs found.")

    def get_stylesheet(self):
        return """
        QMainWindow {
            background-color: #000000;
            color: #00FFFF;
        }
        QLabel {
            color: #00FFFF;
            font-size: 16px;
        }
        QLineEdit {
            background-color: #000000;
            color: #00FFFF;
            border: 1px solid #00FFFF;
            border-radius: 5px;
            padding: 5px;
        }
        QPushButton {
            background-color: #000000;
            color: #00FFFF;
            border: 1px solid #00FFFF;
            border-radius: 5px;
            padding: 8px;
            min-width: 100px;
            font-size: 16px;
        }
        QPushButton:hover {
            background-color: #333333;
            color: #FFFFFF;
            border: 1px solid #FFFFFF;
        }
        QListWidget {
            background-color: #000000;
            color: #00FFFF;
            border: 1px solid #00FFFF;
            border-radius: 5px;
        }
        QProgressBar {
            border: 1px solid #00FFFF;
            border-radius: 5px;
            text-align: center;
            color: white;
        }

        QProgressBar::chunk {
            background-color: #00FFFF;
        }
        QWidget {
            background-color: #000000;
        }
        QHBoxLayout {
            align-items: center;
            justify-content: center;
        }
        """
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TwitterApp()
    window.show()
    sys.exit(app.exec_())
