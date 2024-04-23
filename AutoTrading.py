import sys
import ccxt
import numpy as np
from PyQt5 import QtWidgets, uic


def moving_average(data, window):
    return np.convolve(data, np.ones(window), 'valid') / window


def bollinger_bands(data, window=20, num_std=2):
    ma = moving_average(data, window)
    std = np.std(data[-window:])
    upper = ma + (num_std * std)
    lower = ma - (num_std * std)
    return upper, ma, lower


def check_conditions(ohlcv_data):
    close_prices = ohlcv_data[:, 4]

    ma7 = moving_average(close_prices, 7)
    ma30 = moving_average(close_prices, 30)
    ma90 = moving_average(close_prices, 90)

    upper, _, _ = bollinger_bands(close_prices)

    current_price = close_prices[-1]

    if ma7[-1] > ma30[-1] > ma90[-1] and current_price < upper[-1]:
        return True
    else:
        return False


def get_crypto_list():
    exchange = ccxt.binance()
    markets = exchange.load_markets()
    crypto_list = [symbol for symbol in markets if symbol.endswith('/USDT')]
    return crypto_list


def recommend_crypto(textEdit):
    exchange = ccxt.binance()
    crypto_list = get_crypto_list()

    recommended_list = []

    for symbol in crypto_list:
        ohlcv_data = exchange.fetch_ohlcv(symbol, '1d', limit=100)
        ohlcv_data = np.array(ohlcv_data)

        if check_conditions(ohlcv_data):
            recommended_list.append(symbol)

    textEdit.clear()
    textEdit.append('\n'.join(recommended_list))


class MyWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        uic.loadUi('pythonui.ui', self)

        self.pushButton.clicked.connect(self.search_crypto)

    def search_crypto(self):
        recommend_crypto(self.textEdit)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())