import yfinance as yf
import requests
import json

# Vaše unikátní URL adresa z Make.com webhooku
MAKE_WEBHOOK_URL = "https://hook.eu1.make.com/39jzop9huqq2muljww5goh9wh8rfb32n"

# Seznam top technologických akcií z vašich seznamů
HLIDANE_AKCIE = ['NLST', 'PAYS', 'CXDO', 'BB', 'BLZE', 'TBLA', 'RXT']

def zkontroluj_trh():
    print("Spouštím kontrolu technologických akcií...")
    for ticker in HLIDANE_AKCIE:
        try:
            akcie = yf.Ticker(ticker)
            historie = akcie.history(period="2d")
            
            if len(historie) < 2:
                continue
                
            cena_vcera = historie['Close'].iloc[0]
            cena_dnes = historie['Close'].iloc[1]
            objem_dnes = historie['Volume'].iloc[1]
            
            prumerny_objem = akcie.history(period="10d")['Volume'].mean()
            zmena_procenta = ((cena_dnes - cena_vcera) / cena_vcera) * 100
            
            upozorneni = False
            typ_udalosti = ""
            detail_zpravy = ""
            
            # 1. Propad o více než 5 %
            if zmena_procenta <= -5.0:
                upozorneni = True
                typ_udalosti = "🚨 PROPAD V TRHU (Sleva)"
                detail_zpravy = f"Akcie {ticker} dnes oslabila o {zmena_procenta:.2f}% na cenu ${cena_dnes:.2f}."
                
            # 2. Růst o více než 5 %
            elif zmena_procenta >= 5.0:
                upozorneni = True
                typ_udalosti = "🚀 RAKETOVÝ RŮST"
                detail_zpravy = f"Akcie {ticker} dnes vystřelila o +{zmena_procenta:.2f}% na cenu ${cena_dnes:.2f}."
                
            # 3. Neobvyklý objem (Volume Spike)
            if objem_dnes > (prumerny_objem * 2.0):
                upozorneni = True
                if not typ_udalosti:
                    typ_udalosti = "📈 NEOBVYKLÝ OBJEM (Volume Alert)"
                detail_zpravy += f"\nU akcie {ticker} se dnes obchoduje o {(objem_dnes/prumerny_objem)*100:.0f}% vyšší objem oproti průměru."

            if upozorneni:
                data_k_odeslani = {
                    "vystraha": typ_udalosti,
                    "ticker": ticker,
                    "zprava": detail_zpravy.strip(),
                    "cena": f"${cena_dnes:.2f}"
                }
                
                response = requests.post(
                    MAKE_WEBHOOK_URL, 
                    data=json.dumps(data_k_odeslani), 
                    headers={"Content-Type": "application/json"}
                )
                print(f"Odesláno pro {ticker} s kódem: {response.status_code}")
                
        except Exception as e:
            print(f"Chyba u {ticker}: {e}")
            
    print("Kontrola dokončena.")

if __name__ == "__main__":
    zkontroluj_trh()
  
