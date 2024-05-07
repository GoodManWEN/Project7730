import torch 
import torch.nn as nn
import math

class CNNLSTMATT(nn.Module):

    def __init__(self, seq_len, lstm_units, dim, num_layers, drops):
        super(CNNLSTMATT, self).__init__()
        # 规范化lstm_units为4的倍数
        lstm_units = math.ceil(lstm_units // 4) * 4
        self.conv1d1 = nn.Conv1d(dim, lstm_units//2, 1)
        self.act1 = nn.Sigmoid()
        self.maxPool1 = nn.MaxPool1d(kernel_size=3)
        self.conv1d2 = nn.Conv1d(lstm_units//2, lstm_units, 1)
        self.act2 = nn.Sigmoid()
        self.maxPool2 = nn.MaxPool1d(kernel_size=3)
        self.drops1 = [nn.Dropout(p=0.01) for _ in range(drops)]

        self.lstm = nn.LSTM(lstm_units, lstm_units * 2, batch_first=True, num_layers=num_layers, bidirectional=True)
        self.act3 = nn.Tanh()
        self.maxPool3 = nn.MaxPool1d(kernel_size=7)
        self.bn = nn.BatchNorm1d(lstm_units * 4)

        self.linear = nn.Linear(lstm_units * 8, lstm_units * 4)
        self.act4 = nn.Tanh()
        self.drops2 = [nn.Dropout(p=0.01) for _ in range(drops)]
        self.linear2 = nn.Linear(lstm_units * 4, 2)
        self.act5 = nn.ReLU()

        se_len = seq_len // 3 // 3
        self.se_fc = nn.Linear(se_len, se_len)
        self.hw_fc = nn.Linear(lstm_units, lstm_units)

    def multi_drop(self, x, drops):
        xn = [drop(x) for drop in drops]
        return torch.mean(torch.stack(xn), dim=0)

    def forward(self, x):
        x = x.transpose(-1, -2) 
        x = self.conv1d1(x)
        x = self.act1(x)
        x = self.maxPool1(x)
        x = self.conv1d2(x)
        x = self.act2(x)
        x = self.maxPool2(x)
        x = self.multi_drop(x, self.drops1)

        # channel attention
        avg = x.mean(dim=1)
        se_attn = self.se_fc(avg).softmax(dim=-1)
        x = torch.einsum("bnd,bd->bnd", x, se_attn)

        # height and width attention
        avg = x.mean(dim=2)
        hw_attn = self.hw_fc(avg).softmax(dim=-1)
        x = torch.einsum("bnd,bn->bnd", x, hw_attn)

        x = x.transpose(-1, -2)
        x, (_, _) = self.lstm(x)
        x = self.act3(x)

        x = x.transpose(-1, -2)
        x = self.maxPool3(x)
        x = self.bn(x)

        x = x.view(-1, x.size(1) * x.size(2))
        x = self.linear(x)
        x = self.act4(x)
        x = self.multi_drop(x, self.drops2)
        x = self.linear2(x)
        x = self.act5(x)
        return x
    
class CNNLSTMModel_CBAM(nn.Module):

    def __init__(self, window=5, dim=4, lstm_units=16, num_layers=2):
        super(CNNLSTMModel_CBAM, self).__init__()
        self.conv1d = nn.Conv1d(dim, lstm_units, 1)
        self.act1 = nn.Sigmoid()
        self.maxPool = nn.MaxPool1d(kernel_size=window)
        self.drop = nn.Dropout(p=0.01)
        self.lstm = nn.LSTM(lstm_units, lstm_units, batch_first=True, num_layers=num_layers, bidirectional=True)
        self.act2 = nn.Tanh()
        self.cls = nn.Linear(lstm_units * 2, 1)
        self.act4 = nn.Tanh()

        self.se_fc = nn.Linear(window, window)
        self.hw_fc = nn.Linear(lstm_units, lstm_units)

    def forward(self, x):
        x = x.transpose(-1, -2)  # tf和torch纬度有点不一样
        x = self.conv1d(x)  # in： bs, dim, window out: bs, lstm_units, window
        x = self.act1(x)

        # chanal
        avg = x.mean(dim=1)  # bs, window
        se_attn = self.se_fc(avg).softmax(dim=-1)  # bs, window
        x = torch.einsum("bnd,bd->bnd", x, se_attn)

        # wh
        avg = x.mean(dim=2)  # bs, lstm_units
        hw_attn = self.hw_fc(avg).softmax(dim=-1)  # bs, lstm_units
        x = torch.einsum("bnd,bn->bnd", x, hw_attn)

        x = self.maxPool(x)  # bs, lstm_units, 1
        x = self.drop(x)
        x = x.transpose(-1, -2)  # bs, 1, lstm_units
        x, (_, _) = self.lstm(x)  # bs, 1, 2*lstm_units
        x = self.act2(x)
        x = x.squeeze(dim=1)  # bs, 2*lstm_units
        x = self.cls(x)
        x = self.act4(x)
        return x