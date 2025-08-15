# StackEverything

[切换至中文](../README.md)  
[view on github](https://github.com/ZDZX-T/StackEverything) | [view on gitee](https://gitee.com/ZDZX-T/StackEverything)

## Introduction

Has anyone ever had experiences like this? I remember owning a certain piece of clothing, but I can't recall whether it's at home or at school 🤔. The clothes I neatly folded get messy again every time I search for something 😦. A pile of shoe boxes — to find one specific pair of shoes, you have to open each box, and in the end, you still can’t find it 😠. Meat stored in the fridge during the Spring Festival that isn’t discovered until mid-year 😵…

To solve the problem of "difficulty in finding specific items when things are piled up", I developed the home storage system "StackEverything". Unlike traditional warehouse systems that focus on tracking item quantities, StackEverything focuses on tracking item locations.

With this system, you can track where each item is, like finding your clothes in a pile without digging through everything; You can record medicine expiration dates so you don’t find out they’re expired when you try to use them; You can use it with your family so you don’t have to call for mom when something is missing... In short, this system helps you keep track of anything that gets piled up, so nothing gets lost or forgotten.

## Features

1. **📁Easy-to-use UI**<br/>The main interface is designed similarly to Windows Explorer, which ensures that users are familiar with the operations such as directory switching.<br/>![UI展示](/i18n/img/README_UI.gif)
2. **🕹️Intuitive Interaction**<br/>Drag and drop items to move them, with glowing indicators guiding precise operations.<br/>![移动展示](/i18n/img/README_move.gif)
3. **🪄Multiple Movement Modes**<br/>In addition to basic single-item dragging, StackEverything provides four convenient movement modes: Multi, Insert, Absorb, and Portal. For detailed instructions, please refer to the "Help Document" page inside the system.<br/><img src="/i18n/img/README_multi_quick_en.png" alt="多选快移展示" height="200" style="margin-left: 20px;">
4. **🎛️Custom Classes & Properties**<br/>You can freely add classes and properties for items, making it easier to search for them later.<br/>![分类与属性](/i18n/img/README_attributes_en.png)
5. **🔎Convenience Item Search**<br/>You can search items by name, class, whether they are virtual, expiration date, whether they have children and location. When searching by class, you can further filter results by properties. The fields displayed after filtering can also be customized.<br/>![物品检索](/i18n/img/README_search_en.png)
6. **🛜Access Anywhere on Local Network**<br/>As long as one machine on the local network is running the software, any device connected to the same network can access StackEverything through a web browser, allowing you to take advantage of each device's strengths.<br/><img src="/i18n/img/README_ethernet_en.png" alt="局域网访问" height="300" style="margin-left: 20px;">

## Deployment

_⚠️**Security Warning**: Since this project does not implement an authentication mechanism and uses Flask as its default web server, **do NOT expose this service directly to the public internet**, as it may cause serious security risks._

### First time use

You can obtain this project via `git clone`, or download the latest or specific version from the `Releases` page. This project requires Python>=3.7. After downloading the code, install the required dependencies (flask and pillow) by running the following command in the project directory:

```shell
pip install -r requirements.txt
```

If you want to switch the language to English, set the `LANGUAGE` variable in `config.py` to "en".

Then start the service:

```shell
python StackEverything.py
```

Visit [127.0.0.1:8456](http://127.0.0.1:8456) in your browser to open StackEverything. If accessing from another device, use `host-ip:8456`.
Once the page opens, click the “>” icon in the top-left corner to expand the sidebar menu, and navigate to the “Help Document” page to view the user guide.

Some parameters are user-configurable, such as the language. For a full list of configurable parameters, please refer to [config.py](/config.py).

### Update

You need to protect two files and one folder:

1. `config.py`, this is your configuration file, copied from config_default.py when the system runs for the first time;
2. `_StackEverything.db`, this is the database file, generated after the system runs;
3. `user_image`, this is the folder that stores item images, also generated after the system runs.

#### Manual

Since the files mentioned above do not exist in the source code, simply place the new version's zip package into the StackEverything's directory and extract it to complete the update.  
_Memo: The Linux command for overwriting during extraction is `unzip -o xxx.zip`_

## FAQ

Q1: Does that mean I have to operate your system every time I take out a piece of clothing?  
A1: Not necessarily. For example, I keep my seasonal clothes in a separate pile, and I won’t update the system when I use them. However, during seasonal transitions, it's important to make sure the order of items in the system matches the real-world arrangement — otherwise the system loses its value.

Q2: Isn't your system kind of "butter on bacon"?  
A2: It really depends on personal needs. If you only have a small number of items and can easily remember where everything is, then using this system might indeed feel unnecessary. But when the number of items grows large enough, and the frequency of use becomes low enough, our memory just isn’t reliable anymore — and that’s when tools like this become useful. For example, do you really know what exactly is in that storage room at home right now? With this system, you will — and that’s exactly its purpose.

## Issues / Suggestions

Feel free to submit an Issue. If it's a problem, please describe what you were doing, your directory structure, and any key log information. If it's a suggestion, it would be great to include a use case or explain which current pain points it would solve.

## Sponsorship

If you like this project, you can scan the QR code below with WeChat to give the author some encouragement. Thank you!  
<img src="/i18n/img/sponsor.jpg" alt="赞赏" width="300" height="300">

## Change Log

See [CHANGELOG.md](/CHANGELOG.md)
