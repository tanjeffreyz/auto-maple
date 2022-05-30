
<h2 align="center">
  CUDA, cuDNN, zlib, and environment variable/PATH Setup
</h2>
<ol>
  <li>
    Download and install the latest version of <a href="https://developer.nvidia.com/cuda-downloads">CUDA Toolkit</a>.<br />
      express/default settings are fine
  </li>
  <li>
    Download the latest version of <a href="https://developer.nvidia.com/cudnn">cuDNN</a>, you will need to make a free account for this
  </li>
  <li>
   Place all the cuDNN files in the nvidia toolkit folder for the version you downloaded earlier and replace all files when it asks <br />   
    the default install location should be at "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.7" <br /> 
      Leave this folder open for step 5
  </li>
  <li>
     Download <a href="http://www.winimage.com/zLibDll/zlib123dllx64.zip">zlib</a> and unzip it at "C:\"   <br /> 
      go into the "C:\zlib\dll_x64" folder and leave it open
  </li>
  <li>
Open environment variables, search for "env" next to the taskbar and it should come up <br /> 
    <br /> 
      
![chrome_1T7oinVvK7](https://user-images.githubusercontent.com/16899482/170908758-db921e67-7963-48f8-aee5-56311727662b.jpg)
      
     
      
![unknown(1)](https://user-images.githubusercontent.com/16899482/170906902-b8867b35-3777-4ca0-ad51-89243870b256.jpg)
      
     Environment variables ->  
      
   ![chrome_cyugM6McJ0](https://user-images.githubusercontent.com/16899482/170907962-f2edc0ed-d25c-4961-bba5-100cecd57363.jpg)
   
      Double click on Path -> 
      
![chrome_VDPdMkU77j](https://user-images.githubusercontent.com/16899482/170907999-78370809-d214-4899-96e7-060d73f78c1d.jpg)
      
      Press new -> 

![unknown](https://user-images.githubusercontent.com/16899482/170908120-4fc42fac-304e-494d-ab0c-465abc64793d.jpg)

      Add in the following folders 
      bin & libnvvp from "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.7" 
      and "C:\zlib\dll_x64" 
      press "Ok" to save the changes
      
      CUDA should be properly installed and working for auto maple after this
      
  </li>
  <li>
    https://www.youtube.com/watch?v=hHWkvEcDBO0 Video tutorial if you are still confused after all the steps above <br />
    ( can skip the last few steps, like installing anaconda, tensorflow etc ) <br />
  </li>
    
</ol>




