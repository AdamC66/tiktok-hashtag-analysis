# TikTok Scraper

# About the Project

This project was created in collaboration with Dr. Jennifer Pybus, of York University.
The main project goal was to pull data from TikTok for analysis by students

# Installation

## Step 1: Install Python >3.10:

&nbsp; &nbsp; &nbsp; See: https://www.python.org/downloads/, Exact instructions may vary based on your operating system

If you are using Windows, I highly recommend also setting up [PowerShell](https://learn.microsoft.com/en-us/powershell/scripting/install/installing-powershell-on-windows?view=powershell-7.2)

## Step 2: Download the Project Code:

&nbsp; &nbsp; &nbsp;This can be achieved one of two ways. if you are familiar with GitHub, you may clone this repository onto your local machine. Alternatively you may download the repository as a zip file by selecting the "Code" button on the top right and then selecting "Download ZIP". once you have done that extract the zip file somewhere onto your computer.

## Step 3: Install Requirements

&nbsp; &nbsp; &nbsp; There are two steps to the installation progress. To start, open the project in your terminal. on Mac, this can be done by finding the folder in finder, selecting the folder, then under Finder > Services > selecting "New Terminal At Folder" (See Image Below)

<img src="https://www.maketecheasier.com/assets/uploads/2021/10/launch-any-folder-mac-terminal-new-terminal-at-folder-2.jpg.webp"
     alt="Markdown Monster icon"
     style="display: block; margin: 0 auto" />

On Windows. you can hold shift and right click the folder and select "Open PowerShell Here"

Once you have the terminal open you can enter the following commands

```
> pip install -r requirements.txt
> python -m playwright install
```

Note if you also have Python 2 installed these commands will become

```
> pip3 install -r requirements.txt
> python3 -m playwright install
```

the script should then be ready to run

# Usage

to start the script you'll simply enter

```
> python script.py
```

in your terminal. If All installation worked, you'll then see

```
###########################################
#            TIK TOK SCRAPER              #
###########################################
       Press Ctrl+C/ Cmd+C to Exit

Enter your `s_v_web_id` cookie. see Readme.md for instructions on how to get this value
s_v_web_id:
```

You can retreive your s_v_web_id cookie by:

1. Go to https://www.tiktok.com in your web browser
2. login if you are not. logout and log back in if you are
3. Right click on the page and select "Inspect"
4. In the Inspector, Click "Application" in the top toolbar
5. On the left side under "Storage" select "Cookies", then "https://www.tiktok.com"
6. Copy the value of cookie "s*v_web_id" (it should start with "verify*"), and paste it into the terminal (you will need to right click, and select paste, or use `ctrl/cmd + shift + v`. )

Next you will be asked if you want to perform a search based on hashtag, or by user. you can select by entering "U" for User or "H" for Hashtag, and pressing Enter.

```
Lookup By User(U) or HashTag(H)
H / U? : H
```

You will then be asked to enter your search term, there is no need to add @ or # for hashtags/ users respectively.

```
Enter Search Term
Search : foryoupage
```

OPTIONAL:
This script can also download videos as is collects information. they will be saved as [VideoID].mp4 in the same directory as the script.

```
Should Videos be Downloaded? (This May Take a While)
Y/N: N
```

The script will then begin to scrape through TikTok and search for the user/hashtag entered previously. it will log every 30 videos processed in the terminal so you can track it's progress, this can take a few minutes to complete. if any errors happen during this process, you can press `Ctrl+C/ Cmd+C` to Exit and try again. As this is powered by an unofficial API, searches may not always be successful and you should be prepared to see `TikTokApi.exceptions.TikTokException: 10101 -> TikTok sent an unknown StatusCode of 10101` and have to restart your search

```
Processing . . .
30 Videos processed
60 Videos processed
90 Videos processed
120 Videos processed
150 Videos processed
180 Videos processed
210 Videos processed
240 Videos processed
270 Videos processed
300 Videos processed
330 Videos processed
360 Videos processed
390 Videos processed
420 Videos processed
450 Videos processed
480 Videos processed

Rank     Hashtag                        Occurrences     Frequency
0        fyp                            485             1.0000
1        foryou                         163             0.3361
2        foryoupage                     108             0.2227
3        viral                          93              0.1918
4        xyzbca                         37              0.0763
5        funny                          29              0.0598
6        hilariouspetstiktoktv          23              0.0474
7        fypシ                           23              0.0474
8        fy                             21              0.0433
9        asmr                           21              0.0433
Total posts: 485
```

On completion the script will output a ranking of hashtag frequencies from posts scraped, the rank 0 entry will be your search term.It will also create a JSON file with raw data, and a slightly more organized CSV file. From here you can press `Ctrl+C/ Cmd+C` to exit
