import re
import pandas as pd
import argparse

# Definizione delle sezioni GDPR rilevanti
GDPR_SECTIONS = {
    "Articolo 5(1)(c)": "Minimizzazione dei dati - Raccogli solo i dati necessari.",
    "Articolo 5(1)(e)": "Limitazione della conservazione - Conserva i dati solo per il tempo necessario.",
    "Articolo 6(1)": "Base giuridica - Assicurati di avere una base legale valida per il trattamento.",
    "Articolo 9": "Protezione dei dati sensibili.",
    "Articolo 32": "Sicurezza del trattamento - Protezione dei dati con misure tecniche adeguate.",
    "Articolo 33": "Notifica di violazioni - Devi notificare l'autorità competente in caso di violazione dei dati personali."
}

# Funzione per identificare il tipo di evento nel log applicativo
def identify_application_log_type(line):
    if re.search(r'login|logout|session', line, re.IGNORECASE):
        return "Evento utente"
    elif re.search(r'error|exception|timeout|failed', line, re.IGNORECASE):
        return "Errore o eccezione"
    elif re.search(r'cart|order|purchase|transaction', line, re.IGNORECASE):
        return "Transazione"
    elif re.search(r'config|setting|update|change', line, re.IGNORECASE):
        return "Modifica di configurazione"
    elif re.search(r'api|endpoint|request|response', line, re.IGNORECASE):
        return "Interazione API"
    else:
        return "Evento non identificato"

# Funzione per analizzare i log e suggerire le raccomandazioni GDPR
def parse_application_logs(file_path):
    detected_issues = []
    
    # Leggi il file di log riga per riga
    with open(file_path, 'r') as file:
        lines = file.readlines()  # Legge tutte le righe del file
    
    # Ignora l'intestazione se c'è
    for line in lines[1:]:
        line = line.strip()  # Rimuovi eventuali spazi bianchi o newline
        if not line:  # Salta le righe vuote
            continue

        # Identifica il tipo di log e analizza
        log_type = identify_application_log_type(line)
        
        # Aggiungi logica per identificare problemi e suggerimenti GDPR
        if log_type == "Evento utente":
            match = re.search(r'user_id|session_id|token', line, re.IGNORECASE)
            if match:
                detected_issues.append({
                    "log_type": log_type,
                    "issue": "Credenziali utente o sessioni rilevate",
                    "matched_content": match.group(0),
                    "suggestion": GDPR_SECTIONS["Articolo 5(1)(c)"] + " - Verifica se queste informazioni sono necessarie.",
                    "full_log": line  # Aggiungi l'intero contenuto del log per maggiore contesto
                })
        elif log_type == "Errore o eccezione":
            match = re.search(r'error|exception|failed', line, re.IGNORECASE)
            if match:
                detected_issues.append({
                    "log_type": log_type,
                    "issue": "Errore o eccezione rilevata",
                    "matched_content": match.group(0),
                    "suggestion": GDPR_SECTIONS["Articolo 32"] + " - Assicurati che i log degli errori non contengano dati sensibili.",
                    "full_log": line  # Aggiungi l'intero contenuto del log per maggiore contesto
                })
        elif log_type == "Transazione":
            match = re.search(r'credit card|payment|transaction', line, re.IGNORECASE)
            if match:
                detected_issues.append({
                    "log_type": log_type,
                    "issue": "Transazione finanziaria rilevata",
                    "matched_content": match.group(0),
                    "suggestion": GDPR_SECTIONS["Articolo 9"] + " - Protezione speciale per i dati finanziari.",
                    "full_log": line  # Aggiungi l'intero contenuto del log per maggiore contesto
                })
        elif log_type == "Modifica di configurazione":
            match = re.search(r'config|setting|update', line, re.IGNORECASE)
            if match:
                detected_issues.append({
                    "log_type": log_type,
                    "issue": "Modifica di configurazione rilevata",
                    "matched_content": match.group(0),
                    "suggestion": GDPR_SECTIONS["Articolo 32"] + " - Controlla che le modifiche di configurazione siano sicure.",
                    "full_log": line  # Aggiungi l'intero contenuto del log per maggiore contesto
                })
        elif log_type == "Interazione API":
            match = re.search(r'api|request|response', line, re.IGNORECASE)
            if match:
                detected_issues.append({
                    "log_type": log_type,
                    "issue": "Interazione API rilevata",
                    "matched_content": match.group(0),
                    "suggestion": GDPR_SECTIONS["Articolo 32"] + " - Verifica che le API utilizzino crittografia per proteggere i dati.",
                    "full_log": line  # Aggiungi l'intero contenuto del log per maggiore contesto
                })

    return detected_issues

# Funzione per generare un report dei problemi rilevati
def generate_report(issues):
    # Creiamo un DataFrame includendo tutti i campi, inclusa la parte che ha matchato
    report_df = pd.DataFrame(issues, columns=["log_type", "issue", "matched_content", "suggestion", "full_log"])
    report_df.to_csv('gdpr_application_log_report.csv', index=False)
    print("Report GDPR generato: gdpr_application_log_report.csv")

# Esecuzione del tool
def main():
    # Utilizzo di argparse per accettare il nome del file come argomento
    parser = argparse.ArgumentParser(description="GDPR Log Checker")
    parser.add_argument("log_file", help="Percorso al file di log da analizzare")
    args = parser.parse_args()

    issues = parse_application_logs(args.log_file)
    if issues:
        generate_report(issues)
    else:
        print("Nessun problema rilevato nei log.")

if __name__ == "__main__":
    main()

