import sys
import json
from apis import *
import pandas as pd
from secret import API_KEY
from PySide6.QtCore import QRect, Qt, Signal, Slot
from PySide6.QtWidgets import (
    QLabel,
    QWidget,
    QSpinBox,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QApplication,
    QPlainTextEdit,
)

class MainWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        self.prompt = ''
        self.prompt_le = QLineEdit()
        self.prompt_le.setPlaceholderText('Search prompt...')
        self.prompt_le.textChanged.connect(self.onPromptChanged)

        self.num = 1000
        self.num_sb = QSpinBox()
        self.num_sb.setMaximum(50 * 10000 / 100) # maximum per day
        self.num_sb.setSingleStep(50) # ytb data api's maximum per search
        self.num_sb.setValue(1000) # according to cheuka
        self.num_sb.valueChanged.connect(self.onNumChanged)

        self.search_btn = QPushButton()
        self.search_btn.setText('Search and save')
        self.search_btn.clicked.connect(self.onSearchBtnClicked)

        self.log_pte = QPlainTextEdit()
        self.log_pte.setReadOnly(True)
        self.log_pte.setPlainText('Log...')

        layout.addWidget(self.prompt_le)
        layout.addWidget(self.num_sb)
        layout.addWidget(self.search_btn)
        layout.addWidget(self.log_pte)

        setupYoutubeDataAPI(API_KEY)

    @Slot(str)
    def onPromptChanged(self, new_prompt:str) -> None:
        self.prompt = new_prompt
    
    @Slot(int)
    def onNumChanged(self, new_num:int) -> None:
        self.num = new_num

    @Slot()
    def onSearchBtnClicked(self):
        self.log_pte.setPlainText('')
        
        vids = searchVids(self.prompt, self.num)
        self.log_pte.appendPlainText(f'Fetched {len(vids)} videos')
        channels = filterChannels(vids)
        self.log_pte.appendPlainText(f'Produced by {len(channels)} channels')
        channel_about = []
        for channel_id in channels.keys():
            channel_about.append(getChannelAbout(channel_id))
        data = pd.DataFrame(channel_about)
        data.to_csv('data.csv')
        self.log_pte.appendPlainText(f'CSV generated and saved to "data.csv"')
        self.log_pte.appendPlainText(f'{data}')
    
if __name__ == '__main__':

    app = QApplication(sys.argv)
    main_widget = MainWidget()
    main_widget.show()
    sys.exit(app.exec())
    
