# <h1 align="center"> MAC 108 Project</h1>
My project for Intro to Python (MAC 108) at LaG CC


![Neovim](https://img.shields.io/badge/Editor-Neovim-57A143?logo=neovim)
![Python](https://img.shields.io/badge/Python-3.14%2B-blue?logo=python) 
![License](https://img.shields.io/badge/license-_MIT_-fb542b)
![Static Badge](https://img.shields.io/badge/BTW-Arch?style=plastic&logo=archlinux&logoColor=%231793D1&labelColor=black&color=%231793D1)


## Planning  


### Scripting  

- Create a file to parse auth logs for failed attempts and identify patterns

    - detect abnormal hours
    - flag unknown IPs
    - ID signs of brute force attack
    - IF creating a cloud instance -- EC2 ubuntu machine -- logs located /var/log/ 

- Call an alerting script for suspiscious activity listed above
    - email/text notification blast
        - find a service if possible

- Print incoming alerts in an open montioring terminal

- Summary generator
    - Reporting of events
    - show trends of repeat IP offenders
    - matplotlib to graph trends for presentation

---

### Video Presentation  

Guidelines:
- PPT Slides (No more than 5)
- Max 10 min video, visible the whole time


---

### Network/Attack Surface
- Options:

    - Set up a honeypot on azure or aws
        - Pros: Can set up a true SIEM to compare outcomes 
        - Cons: Might get expensive if not monitored closely
    
    - Create a VLAN on home network and simulate attacks
        - Easier to implement
        - No "real" hands-on experience
    
    - Use my existing web domain in some way?
        - No idea how to go about this, will have to consult a lot of documentation. 

