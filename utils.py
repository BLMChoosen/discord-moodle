from datetime import datetime
import re

MESES_PT = {
    'jan.': '01', 'fev.': '02', 'mar.': '03', 'abr.': '04', 'mai.': '05', 'jun.': '06',
    'jul.': '07', 'ago.': '08', 'set.': '09', 'out.': '10', 'nov.': '11', 'dez.': '12'
}

def parse_moodle_date(date_str):
    """
    Converte uma string de data do Moodle em português para datetime.
    Retorna None se a data for inválida ou já vencida.
    """
    if not date_str or '-' == date_str.strip() or date_str.strip() == '':
        return None
    try:
        # Remove o dia da semana (antes da vírgula)
        if ',' in date_str:
            date_str = date_str.split(',', 1)[1].strip()
        # Ex: '29 mai. 2025, 00:00'
        m = re.match(r'(\d{1,2}) (\w{3,4}\.) (\d{4}), (\d{2}):(\d{2})', date_str)
        if m:
            dia, mes_pt, ano, hora, minuto = m.groups()
            mes = MESES_PT.get(mes_pt.lower())
            if not mes:
                return None
            dt = datetime(int(ano), int(mes), int(dia), int(hora), int(minuto))
            # Só retorna None se o prazo já passou (data e hora)
            if dt < datetime.now():
                return None
            return dt
        # Ex: '29 mai. 2025'
        m = re.match(r'(\d{1,2}) (\w{3,4}\.) (\d{4})', date_str)
        if m:
            dia, mes_pt, ano = m.groups()
            mes = MESES_PT.get(mes_pt.lower())
            if not mes:
                return None
            dt = datetime(int(ano), int(mes), int(dia))
            # Considera vencido só se a data já passou (hoje ainda vale)
            if dt.date() < datetime.now().date():
                return None
            return dt
        # Tenta formatos padrões
        for fmt in ("%d/%m/%Y %H:%M", "%d/%m/%Y", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
            try:
                dt = datetime.strptime(date_str, fmt)
                if fmt.endswith("%H:%M"):
                    if dt < datetime.now():
                        return None
                else:
                    if dt.date() < datetime.now().date():
                        return None
                return dt
            except Exception:
                continue
    except Exception:
        pass
    return None
