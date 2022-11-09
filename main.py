import sys
import json
import datetime
from apis import *
import pandas as pd
from secret import API_KEY
from PySide6.QtCore import QRect, Qt, Signal, Slot
from PySide6.QtWidgets import *
class MainWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QGridLayout(self)
        self.prompt = ''
        self.prompt_le = QLineEdit()
        self.prompt_le.setPlaceholderText('Search prompt...')
        self.prompt_le.textChanged.connect(self.onPromptChanged)

        self.filters_kwargs = {
            'order': 'viewCount',
            'publishedAfter': self._timeMinus('this month')
        }

        self.filters_order_cb = QComboBox()
        self.filters_order_cb.addItems(
            ['relevance', 'date', 'viewCount', 'rating'])
        self.filters_order_cb.setCurrentText('viewCount')
        self.filters_order_cb.currentIndexChanged.connect(self.onFilterChanged)
                
        self.filters_uploadtime_cb = QComboBox()
        self.filters_uploadtime_cb.addItems(
            ['any time', 'this hour', 'today', 
            'this week', 'this month', 'this year'])
        self.filters_uploadtime_cb.setCurrentText('this month')
        self.filters_uploadtime_cb.currentIndexChanged.connect(self.onFilterChanged)    
        
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

        layout.addWidget(self.prompt_le, 0, 0, 1, 2)
        
        layout.addWidget(QLabel('Sort by:'), 1, 0)
        layout.addWidget(self.filters_order_cb, 1, 1)

        layout.addWidget(QLabel('Uploaded in:'), 2, 0)
        layout.addWidget(self.filters_uploadtime_cb, 2, 1)
        
        layout.addWidget(QLabel('Number of videos:'), 3, 0)
        layout.addWidget(self.num_sb, 3, 1)
        layout.addWidget(self.search_btn, 4, 0, 1, 2)
        layout.addWidget(self.log_pte, 5, 0, 1, 2)
            

        setupYoutubeDataAPI(API_KEY)

    @Slot(str)
    def onPromptChanged(self, new_prompt:str) -> None:
        self.prompt = new_prompt
    
    @Slot(int)
    def onNumChanged(self, new_num:int) -> None:
        self.num = new_num

    @Slot()
    def onSearchBtnClicked(self) -> None:
        self.log_pte.setPlainText('Searching...')
        
        vids = searchVids(self.prompt, self.num, self.filters_kwargs)
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

    def _timeMinus(self, diff: str) -> str:
        kwargs = {}
        if diff == 'this hour':
            kwargs['hours'] = 1
        elif diff == 'today':
            kwargs['days'] = 1
        elif diff == 'this week':
            kwargs['weeks'] = 1
        elif diff == 'this month':
            kwargs['days'] = 30
        elif diff == 'this year':
            kwargs['days'] = 365
        return (datetime.datetime.now() - datetime.timedelta(**kwargs)) \
            .astimezone().replace(microsecond=0).isoformat()

    @Slot()
    def onFilterChanged(self) -> None:
        self.filters_kwargs['order'] = self.filters_order_cb.currentText()
        self.filters_kwargs['publishedAfter'] = \
            self._timeMinus(self.filters_uploadtime_cb.currentText()) \
                if self.filters_uploadtime_cb.currentText() != 'any time' \
                else None    

    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_widget = MainWidget()
    main_widget.show()
    sys.exit(app.exec())
    
