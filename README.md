<h1 align="center">
  Auto Maple (自動楓之谷)
</h1>

Auto Maple 是一款智慧型 Python AI，專門為 2D 橫向捲軸 MMORPG《楓之谷》（MapleStory）設計。它結合了模擬按鍵輸入、TensorFlow 機器學習、OpenCV 範本匹配以及多項電腦視覺技術。

由社群建立的資源，例如各職業的 **指令書 (Command Books)** 以及各張地圖的 **腳本 (Routines)**，可以在 **[資源儲存庫](https://github.com/tanjeffreyz/auto-maple-resources)** 中找到。

<br>

<h2 align="center">
  小地圖 (Minimap)
</h2>

<table align="center" border="0">
  <tr>
    <td>
Auto Maple 使用 <b>OpenCV 範本匹配</b> 技術來確定小地圖的邊界以及其中的各種元素，從而精準追蹤玩家在遊戲中的位置。如果將 <code>record_layout</code> (紀錄地形) 設定為 <code>True</code>，Auto Maple 會將玩家之前的座標記錄在一個基於 <b>四元樹 (Quadtree)</b> 的地形物件中。程式會利用 <b>A* 搜尋演算法</b> 來計算玩家到目標位置的最短路徑，這能顯著提高執行腳本的速度與準確性。
    </td>
    <td align="center" width="400px">
      <img align="center" src="https://user-images.githubusercontent.com/69165598/123177212-b16f0700-d439-11eb-8a21-8b414273f1e1.gif"/>
    </td>
  </tr>
</table>

<br>

<h2 align="center">
  技能指令書 (Command Books)
</h2>

<p align="center">
  <img src="https://user-images.githubusercontent.com/69165598/123372905-502e5d00-d539-11eb-81c2-46b8bbf929cc.gif" width="100%"/>
  <br>
  <sub>
    上圖展示了 Auto Maple 穩定地執行一套高難度的技能組合。
  </sub>
</p>
  
<table align="center" border="0">
  <tr>
    <td width="100%">
本程式採用模組化設計，只要提供「指令書」，Auto Maple 就能操作遊戲中的任何角色。指令書是一個 Python 檔案，包含多個類別（代表不同的遊戲技能），定義了應按下的按鍵及時機。指令可以直接存取 Auto Maple 的全域變數，從而根據玩家位置與遊戲狀態改變行為。
    </td>
  </tr>
</table>
  
<br>

<h2 align="center">
  動作腳本 (Routines)
</h2>

<table align="center" border="0">
  <tr>
    <td width="350px">
      <p align="center">
        <img src="https://user-images.githubusercontent.com/69165598/150469699-d8a94ab4-7d70-49c3-8736-a9018996f39a.png"/>
        <br>
        <sub>
          點擊 <a href="https://github.com/tanjeffreyz02/auto-maple/blob/f13d87c98e9344e0a4fa5c6f85ffb7e66860afc0/routines/dcup2.csv">這裡</a> 查看完整腳本範例。
        </sub>
      </p>
    </td>
    <td>
腳本是一個由使用者建立的 CSV 檔案，用來告訴 Auto Maple 在每個地點應如何移動及使用哪些指令。內建的編譯器會解析 CSV 並將其轉換為可執行的物件清單。
<br><br>
以下是常用的腳本組件摘要：
<ul>
  <li>
    <b><code>Point (座標點)</code></b>：角色進入誤差範圍時執行其下方的指令。支援 <code>adjust</code> (精細微調)、<code>frequency</code> (執行頻率) 等設定。
  </li>
  <li>
    <b><code>Label (標籤)</code></b>：用於組織腳本區塊或建立迴圈的參考點。
  </li>
  <li>
    <b><code>Jump (跳轉)</code></b>：直接跳轉到指定的標籤位置執行。
  </li>
  <li>
    <b><code>Setting (設定)</code></b>：動態更新特定設定值（如移動誤差範圍）。
  </li>
</ul>
    </td>
  </tr>
</table>

<br>

<h2 align="center">
  自動解輪 (Runes)
</h2>

<p align="center">
  <img src="https://user-images.githubusercontent.com/69165598/123479558-f61fad00-d5b5-11eb-914c-8f002a96dd62.gif" width="100%"/>
</p>

<table align="center" border="0">
  <tr>
    <td width="100%">
Auto Maple 能夠自動破解遊戲中的「輪」箭頭謎題。它首先使用 OpenCV 分離箭頭並減少雜訊，接著使用預先訓練好的 <b>TensorFlow</b> 模型進行推論，確保在混亂的環境中也能準確解題。
    </td>
  </tr>
</table>

<br>

<h2 align="center">
  環境架設與快速啟動
</h2>

對於完全沒有程式經驗的新手，請按照以下步驟操作：

<ol>
  <li>
    下載並安裝 <a href="https://www.python.org/downloads/">Python 3</a>。
  </li>
  <li>
    下載並安裝最新版本的 <a href="https://developer.nvidia.com/cuda-downloads">CUDA Toolkit</a> (用於 AI 加速)。
  </li>
  <li>
    下載並解壓縮最新版本的 <a href="https://github.com/tanjeffreyz02/auto-maple/releases">Auto Maple 釋出檔</a>。
  </li>
  <li>
    下載 <a href="https://drive.google.com/drive/folders/1SPdTNF4KZczoWyWTgfyTBRvLvy7WSGpu?usp=sharing">TensorFlow 模型</a> 並將「models」資料夾放進 <code>assets</code> 目錄中。
  </li>
  <li>
    <b>無腦啟動法：</b> 在程式主目錄下建立一個名為 <code>啟動程式.bat</code> 的檔案，並貼入以下內容，以後只需點兩下即可執行：
  </li>
</ol>

<pre><code>@echo off
echo [第一步] 正在自動安裝所需的 Python 工具...
python -m pip install -r requirements.txt
echo [第二步] 正在啟動程式...
python main.py
pause</code></pre>

<br>

<h2 align="center">
  🛠️ 如何設定你的自動程式？
</h2>

<h3>程式快捷鍵控制 (Auto Maple Controls)：</h3>
<ul>
  <li><b>Start/stop (啟動/停止)</b>：預設是鍵盤上的 <code>Insert</code>。按下去後程式會變綠色並開始運作。</li>
  <li><b>Reload routine (重載腳本)</b>：如果你修改了腳本內容，按一下 <code>F6</code> 即可套用新設定，不用重開程式。</li>
  <li><b>Record position (紀錄座標)</b>：走到遊戲中的某個點，按 <code>F7</code>，程式就會把座標記下來，方便你寫腳本。</li>
</ul>

<h3>遊戲內按鍵設定 (In-game Keybindings)：</h3>
<ul>
  <li>在這裡輸入你在遊戲中「拾取/互動」與「寵物飼料」的按鍵。</li>
  <li><b>注意</b>：請確保這裡的設定與你遊戲內的快捷鍵一模一樣。</li>
</ul>

<h3>寵物自動餵食 (Pets)：</h3>
<ul>
  <li><b>啟用自動餵食</b>：打勾後，程式每隔一段時間就會自動按一下飼料鍵。</li>
  <li><b>寵物數量</b>：你有幾隻寵物就選幾隻。程式會聰明地幫你計算，寵物越多，餵食次數就會越頻繁，保證牠們不會餓死。</li>
</ul>

<h3>職業專屬按鍵：</h3>
<ul>
  <li>當你從 <b>檔案 -> 讀取指令</b> 選好職業後，右側會出現該職業所有的技能按鍵設定。</li>
  <li>你可以在這裡把程式預設的按鍵改造成你習慣的遊戲按鍵，改完記得點選「儲存」。</li>
</ul>

<br>

<h2 align="center">
  💡 無腦執行小撇步
</h2>

<ul>
  <li><b>「儲存」按鈕很重要</b>：在介面上改完按鍵後，一定要點一下下方的 <b>「Save (儲存)」</b>，設定才會生效。</li>
  <li><b>不要在運行中修改</b>：如果你已經按下 <code>Insert</code> 啟動了自動程式，請先按一下停止，再進行按鍵修改，這樣才安全。</li>
  <li><b>看到英文不要怕</b>：控制台（黑色視窗）現在會印出像 <code>[~] 正在自動安裝...</code> 這樣的中文提示，只要照著提示做就好！</li>
</ul>

<br>

<h2 align="center">
  影片示範
</h2>

<p align="center">
  <a href="https://youtu.be/iNj1CWW2--8?si=MA4n6EAHokI9FX8B"><b>點擊下方觀看完整示範影片</b></a>
</p>

<p align="center">
  <a href="https://youtu.be/iNj1CWW2--8?si=MA4n6EAHokI9FX8B">
    <img src="https://user-images.githubusercontent.com/69165598/123308656-c5b61100-d4d8-11eb-99ac-c465665474b5.gif" width="600px"/>
  </a>
</p>
