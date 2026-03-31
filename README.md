# ◈ Half Time News
A personal news aggregator that uses rss and clustering to have all preferred news in the same place, sources from where i get the news
are hardcoded inside fetcher.py and can be changed in any way.

## Developement and Prerequisites
The program is composed by a main python file and it has been implemented on ubuntu using venv. To replicate my setup, clone this repository, setup venv and activate it inside the desired folder with this command:
```bash
git clone https://github.com/4Ies/newsagg.git
cd newsagg
python3 -m venv venv
source venv/bin/activate
```
All the used python libraries can be installed using the `pip install` command followed by what's inside the `requirements.txt`:
```bash
pip install -r requirements.txt
```

To finally run the program, simply:
```bash
python main.py
```

## Roadmap

🟡 - in WIP

- [🟡] Add settings tab with possibility to insert custom RSS and sections
- [🟡] GUI background and styling improvement
---