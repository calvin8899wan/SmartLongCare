1. 作品應用主題: MyWay智能擺位幫手
2. 選用硬體: Xilinx_PYNQZ2、Mouser Camera
3. 選料說明:
    1. Xilinx_PYNQZ2: 開發可用Python，方便撰寫。
    2. Mouser Camera: 具有1080p的解析度，可以拍攝出清晰的圖像。
4. 硬體連結架構圖: <br/>
    ![](https://i.imgur.com/BmQxyFE.jpg)
5. 程式碼說明: <br/>
    PC Req: pytorch>=1.8.0、tensorboardX>=2.2、opencv、matplotlib、yacs. <br/>
    若要在Xilinx_PYNQZ2上執行需安裝PyTorch、tensorboardX>=2.2、opencv、matplotlib、yacs. <br/>
    在repo中建立一個model資料夾並下載[預訓練權重](https://drive.google.com/file/d/1_rK0NMNGNtJi_8S1Pxw7HxEVtpCQ4Hk4/view?usp=sharing)放置於model資料夾中<br/>
    需切換工作路徑至與CPU17.py同層資料夾中
    - CPU17.py: AI運算檔
    - get_img.py: 擷取攝像頭的影像進行運算
    - example.py: 範例檔，抓取repo_root/data裡的測試圖進行運算
