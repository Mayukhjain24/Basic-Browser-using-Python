import sys
import logging
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import (QApplication, QMainWindow, QToolBar, QAction, QLineEdit, 
                             QTabWidget, QFileDialog, QMessageBox, QMenu)
from PyQt5.QtGui import QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class BrowserTab(QWebEngineView):
    def __init__(self, *args, **kwargs):
        super(BrowserTab, self).__init__(*args, **kwargs)
        self.page().titleChanged.connect(self.update_title)

    def update_title(self):
        self.setWindowTitle(self.page().title())

    def contextMenuEvent(self, event):
        menu = QMenu(self)

        # Add standard navigation actions
        menu.addAction(self.pageAction(QWebEnginePage.Back))
        menu.addAction(self.pageAction(QWebEnginePage.Forward))
        menu.addAction(self.pageAction(QWebEnginePage.Reload))
        menu.addAction(self.pageAction(QWebEnginePage.Stop))

        # Add Inspect Element action
        inspect_element_action = QAction("Inspect Element", self)
        inspect_element_action.triggered.connect(self.inspect_element)
        menu.addAction(inspect_element_action)

        # Add Save Page As action
        save_page_action = QAction("Save Page As...", self)
        save_page_action.triggered.connect(self.save_page_as)
        menu.addAction(save_page_action)

        menu.exec_(event.globalPos())

    def inspect_element(self):
        # Open the developer tools in a new window
        self.page().view().page().devToolsPage().show()

    def save_page_as(self):
        file_dialog = QFileDialog(self, "Save Page As")
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setNameFilter("HTML Files (*.html *.htm)")
        file_dialog.setDefaultSuffix("html")
        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()[0]
            self.page().toHtml(lambda html: self.save_html(html, file_path))

    def save_html(self, html, file_path):
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(html)
            QMessageBox.information(self, "Success", "Page saved successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while saving the page: {str(e)}")

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Web Browser")
        self.setGeometry(100, 100, 1000, 600)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)

        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)

        back_btn = QAction(QIcon.fromTheme("go-previous"), "Back", self)
        back_btn.triggered.connect(self.navigate_back)
        self.toolbar.addAction(back_btn)

        forward_btn = QAction(QIcon.fromTheme("go-next"), "Forward", self)
        forward_btn.triggered.connect(self.navigate_forward)
        self.toolbar.addAction(forward_btn)

        reload_btn = QAction(QIcon.fromTheme("view-refresh"), "Reload", self)
        reload_btn.triggered.connect(self.reload_page)
        self.toolbar.addAction(reload_btn)

        home_btn = QAction(QIcon.fromTheme("go-home"), "Home", self)
        home_btn.triggered.connect(self.navigate_home)
        self.toolbar.addAction(home_btn)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.toolbar.addWidget(self.url_bar)

        new_tab_btn = QAction(QIcon.fromTheme("tab-new"), "New Tab", self)
        new_tab_btn.triggered.connect(lambda checked: self.add_new_tab())
        self.toolbar.addAction(new_tab_btn)

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&File")
        new_tab_action = QAction("New Tab", self)
        new_tab_action.triggered.connect(lambda checked: self.add_new_tab())
        file_menu.addAction(new_tab_action)

        self.add_new_tab()

    def add_new_tab(self, qurl=None, label="Blank"):
        logging.debug("Adding new tab")
        if qurl is None or isinstance(qurl, bool):
            qurl = QUrl("http://www.google.com")
        elif isinstance(qurl, str):
            qurl = QUrl(qurl)

        try:
            browser = BrowserTab()
            browser.setUrl(qurl)
            
            i = self.tabs.addTab(browser, label)
            self.tabs.setCurrentIndex(i)

            browser.urlChanged.connect(lambda qurl, browser=browser: self.update_urlbar(qurl, browser))
            browser.loadFinished.connect(lambda _, i=i, browser=browser: self.tabs.setTabText(i, browser.page().title()))
            
            logging.debug("New tab added successfully")
        except Exception as e:
            logging.error(f"Error adding new tab: {str(e)}")
            QMessageBox.critical(self, "Error", f"An error occurred while adding a new tab: {str(e)}")

    def close_tab(self, i):
        if self.tabs.count() < 2:
            return
        self.tabs.removeTab(i)

    def update_urlbar(self, q, browser=None):
        if browser != self.tabs.currentWidget():
            return
        self.url_bar.setText(q.toString())
        self.url_bar.setCursorPosition(0)

    def navigate_home(self):
        self.tabs.currentWidget().setUrl(QUrl("http://www.google.com"))

    def navigate_to_url(self):
        q = QUrl(self.url_bar.text())
        if q.scheme() == "":
            q.setScheme("http")
        self.tabs.currentWidget().setUrl(q)

    def navigate_back(self):
        try:
            self.tabs.currentWidget().back()
        except Exception as e:
            logging.error(f"Error navigating back: {str(e)}")

    def navigate_forward(self):
        try:
            self.tabs.currentWidget().forward()
        except Exception as e:
            logging.error(f"Error navigating forward: {str(e)}")

    def reload_page(self):
        try:
            self.tabs.currentWidget().reload()
        except Exception as e:
            logging.error(f"Error reloading page: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Browser()
    window.show()
    sys.exit(app.exec_())
