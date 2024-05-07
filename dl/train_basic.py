import torch
from torch.utils.data import DataLoader 
from dataloader import MyDataset
from models import CNNLSTMATT, CNNLSTMModel_CBAM
import torch.nn as nn
import numpy as np
from loguru import logger
from pipeit import *

EPOCH_LIMIT = 999
LEANRNING_RATE = 0.01

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

train_data = MyDataset(data_folder='D:\\Test\\train_data', seq_len=128, feature_len=5, io1=10, mode='TRAIN')
# test_data = MyDataset(data_folder='D:\\Test\\test_data', seq_len=128, feature_len=5, io2=1, mode='TEST')

train_loader = DataLoader(train_data, batch_size=128, shuffle=True)
# test_loader = DataLoader(test_data, batch_size=128, shuffle=False)

# model = CNNLSTMATT(seq_len=128, lstm_units=128, dim=5, num_layers=2, drops=7).to(device)
model = CNNLSTMModel_CBAM(window=128, dim=5, lstm_units=32, num_layers=2).to(device)
criterion = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=LEANRNING_RATE)


# for step, (data, label) in enumerate(train_loader):
#     # 将data转化到numpy对象
#     data = data.numpy()
#     label = label.numpy()
#     # 缓存数据
#     with open('data.npy', 'wb') as f:
#         np.save(f, data)
#     with open('label.npy', 'wb') as f:
#         np.save(f, label)
#     break

for epoch in range(EPOCH_LIMIT):
    # logger.info(f'Epoch: {epoch}')
    
    model.train()
    for step, (data, label) in enumerate(train_loader):
        data = data.to(device)
        label = label.to(device)
        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, label)
        loss.backward()
        optimizer.step()

    if epoch % 1 == 0:
        logger.info(f'Epoch: {epoch}, Loss: {loss.item()}')

    if epoch % 10 == 9:
        torch.save(model.state_dict(), f'model_{epoch}.pth')