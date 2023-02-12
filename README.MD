# SBI PDF Downloader

> This is a python crawler project that can automatically scrape the trading notification PDF files issued by SBI Securities.

## 1. Install

```bash
pdm install
```

## 2. Usage
> You can modify the .env file from .env.example. The fist time you can set env FETCH_ALL=true. After that you can set it to false.

```bash
pdm run sbi
```

## 3. Crontab schedule

```
0 17 * * * cd YOUR_SRC_DIR && pdm run sbi
```
