from pprint import pprint
import csv
from datetime import datetime, timedelta, date, time
import re 


def validation_of_rows(input_list):

    # funkcja sprawdzajaca poprawnosc wpisanych danych
    # jesli ktorys z wierzy nie bedzie pasowal do okreslonego
    # formatu, funkcja zwroci blad

    i_date = 0
    i_event = 1
    i_gate  = 2

    for row in input_list:

        if row == []:       # jesli mamy pusty wiersz to go usun
            input_list.remove(row)
        
        else:

            # format daty
            try:
                datetime.strptime(row[i_date], '%Y-%m-%d %H:%M:%S ')
            except ValueError as err:
                print(err)

            # format eventu
            pattern_event = re.compile(r'Reader (exit|entry)')

            matched_event = re.match(pattern_event, row[i_event])
            is_matched_event = bool(matched_event)

            if is_matched_event is False:
                raise ValueError(f'Event data does not match format: Reader (exit|entry)')

            #format bramki
            pattern_gate = re.compile(r'^E/[0-3]/KD1/[0-9]-[0-9]$')

            matched_gate = re.match( pattern_gate, row[i_gate])
            is_matched_gate = bool(matched_gate)

            if is_matched_gate is False:
                raise ValueError(f'Data Gate does not match format: E/[0-3]/KD1/[0-9]-[0-9]')

def is_this_correct_time(now, before):

    # funkcja sprawdza poprawnosc wprowadzonych godzin
    # w pliku wejsciowym, jesli rozpatrywana godzina
    # bedzie "mniejsza" niz poprzednia tego samego dnia
    # ustawi flage 'inconclusive'

    # konwersja na typ timedela aby moc porownac aktualnie 
    # rozpatrywana godzine z ostantio rozpatrywana godzine
    # aby wykryc ewentualne bledy z godzinami

    # czy sa to te same dni
    if now.date() == before.date():
        fomated_time = now.time()
        ls = before.time()

        # formated_time_timedelta
        fr_td = timedelta(hours=formated_time.hour, minutes=formated_time.minute, seconds= formated_time.second)
        # last_timedelta
        ls_td = timedelta(hours=ls.hour, minutes=ls.minute, seconds= ls.second)

        # jesli nie to ustaw flage "inconclusive"
        if fr_td < ls_td:
            dict_of_days[formated_date]['flags']['inconclusive'] = "i "
            #raise ValueError(f"Time of day {formated_date} - {fr_td} is earlier than the previous one : {ls_td}")



def substract_datetime(start, end):
    # funkcja odejmujaca od siebie dwie podane godziny, zwraca obiekt timedelta

    tmp_date = date(1,1,1)
    start = datetime.combine( tmp_date, start )
    end = datetime.combine( tmp_date, end )

    return end - start

def get_sum_of_time(day):

    # funkcja przypisuje atrybutowi 'sum_of_work' rozpatrywanego
    # dnia w slowniku dni dict_of_days sume calego czasu 
    # przepracowanego w biurze 

        # zmienna odpowiedzialna za przechowanie sumy czasu
        # wszystkich partii pracy
        sum_of_all_batch = timedelta(seconds=0)
        
        # ilosc "partii" w ktorych przebywal w biurze
        number_of_batches = len(list(day['batches_of_time_in'].keys()))


        # jesli tego dnia nie przebywal w biurze 
        if ( number_of_batches == 0 ):
            day['flags']['inconclusive'] = "i "
            day['sum_of_work'] =  timedelta(seconds = 0)

        # jesli tego dnia przebywal w biurze
        else:
            # wykonaj dla kazdej parti pracy
            for index in range(1,number_of_batches+1):
                
                # przypisujemy do zmiennych konkretne godzinowe wartosci wejscia
                # i wyjscia do/z budynku
                start_work = day['batches_of_time_in'][index][_entry]
                end_work = day['batches_of_time_in'][index][_exit]
                    
                # suma jednej partii
                sum_of_one_batch = substract_datetime(start_work, end_work)
                sum_of_all_batch += sum_of_one_batch

            # zapisujemy w slowniku konkretnego dnia ilosc czasu spedzonego w biurze
            day['sum_of_work'] =  timedelta(seconds = sum_of_all_batch.seconds)


def get_last_days(dict_of_days):

    # funkcja obliczajaca ktore dni w podanych danych sa ostatnimi dniami danego
    # tygodnia, dostaje wczesniej utworzony slownik ze wszystkimi podanymi na 
    # wejsciu przepracowanymi dniami i zwraca kolejny slownik tylko ostatnich
    # dni tygodnia

    dict_of_last_days = dict()  # tworzymy nowy slownik

    last_day = list(dict_of_days.keys())[0] # zapisujemy w zmiennej pierwszy
                                            # rozpatrywany dzien

    week_of_last_day = last_day.isocalendar()[1]

    dict_of_last_days[week_of_last_day] = last_day

    for day in dict_of_days:

        week_of_last_day = last_day.isocalendar()[1] #zwraca tydzien w ktotrym znajduje sie ten dzien
        week_of_this_day = day.isocalendar()[1]      #to samo tylko dla rozpatrywanego dnia

        # jesli rok jest ten sam i jesli tydzien jest ten sam
        if day.year == last_day.year and week_of_last_day ==  week_of_this_day :
                
            #numer dnia w tygodniu danego dnia jest wiekszy od "ostatniego", np: czwartek > wtorku
            if day.weekday() >= dict_of_last_days[week_of_last_day].weekday():
                # zamien ostatni dzien na aktualnie rozpatrywany pod tym kluczem 
                dict_of_last_days[week_of_last_day] = day
                # i zmienna last_day ustaw na rozpatrywany dzien
                last_day = day
            
        else:
            #jesli sa z roznych lat lub roznych tygodni 
            # to stworz nowy klucz z tym dniem
            dict_of_last_days[week_of_this_day] = day
            # i przypisz do zmiennej last_day
            last_day = day


    return dict_of_last_days


def get_weekly_time_of_work(dict_of_days, dict_of_last_days, day):

    # funkcja obliczajaca ilosc przepracowanego czasu w calym tygodniu od dnia podanego
    # w 'day', ze wszystkich podanych mu dni zapisanych w pierwszym podawanym slowniku
    # zliczy przepracowany czas od poczatku danego tygodnia pracy (niekoniecznie
    # poniedzialku, dowolnie) do konca (rowniez dowolnie)
  
        

        counter_of_working_days = 0             # licznik przepracowanych dni

        weekly_time_of_work = timedelta(seconds=0)  # zmienna przechowujaca przepracowany 
                                                    # czas w sekundach ustawiona na zero
        
        days_to_Monday = day.weekday()       # zmienna wskazuje od jakiego dnia tygodnia 
                                             # "zaczynamy" sprawdzac ilosc dni
        
        next_day = timedelta(days=1)         # ta zmienna bedziemy przechodzic po kolejnych dniach

        week_day = day - timedelta(days=days_to_Monday)   # zaczynamy od poniedzialku - weekday() = 0

        while week_day != (day+next_day):       # dopoki nie dojdzie do ostatniego dnia
            
            if week_day in dict_of_days.keys():      # sprawdzamy czy ten dzien jest w slowniku

                sum_of_work = dict_of_days[week_day]['sum_of_work']  # zmienna przechowuje ilosc pracy 
                                                                     # danego dnia w sekndach
                
                weekly_time_of_work += sum_of_work      # czas pracy w sekunach jest zliczany w zmiennej

                counter_of_working_days += 1        # licznik przepracowanych dni zwiekszany o 1

            week_day = week_day + next_day      # przesuwamy na nastepny dzien

        normal_time_of_work = 8 * counter_of_working_days   # na podstawie ilosci dni sprawdzamy
                                                            # ile godzin powinien przepracowac
        
        return weekly_time_of_work, normal_time_of_work     # zwracamy tygodniowy czas pracy i
                                                            # ile godzin powinien przepracowac

def timedelta_to_HMS(time_delta_data):

    # funkcja konwertujaca obiekt 'timedelta' (ktory automatycznie wyswiela
    # podany czas w optymalnej postaci, tj. jesli jest wiecej niz 24h to
    # zaczyna dopisywac dni) w zmienne odpowiadajace konkretnym danym
    # czasowym ktore sa umieszczane w formie zwyklego stringa
    # funkcja zwraca rowniez w postaci listy te wpisane dane aby
    # mozna bylo na nich pozniej wykonywac operacje 

    w_data = list()     # lista ktora bedzie przechowywac dane o:
    w_hours = 0         # - godzinach
    w_min = 0           # - minutach
    w_sec = 0           # - sekundach
                         

    if time_delta_data.seconds == 0 and time_delta_data.days == 0:
        
        return "00:00:00"

    if time_delta_data.days == 0 or time_delta_data.days == 1:
        
        w_hours += time_delta_data // timedelta(hours=1)
        w_min += (time_delta_data - timedelta(hours=w_hours)) // timedelta(minutes=1)
        w_sec += (time_delta_data - timedelta(hours=w_hours, minutes=w_min)) // timedelta(seconds=1)


    elif time_delta_data.days > 1:
        for i in range(time_delta_data.days - 1):
            w_hours += time_delta_data // timedelta(hours=1)
            w_min += (time_delta_data - timedelta(hours=w_hours)) // timedelta(minutes=1)
            w_sec += (time_delta_data - timedelta(hours=w_hours, minutes=w_min)) // timedelta(seconds=1)
        
    
    f_HMS = f"{w_hours:02}:{w_min:02}:{w_sec:02}"


    return f_HMS





with open('input.csv', 'r') as input_file:
    try:
        input_read = csv.reader(input_file, delimiter=';')
    except ValueError:
        raise ValueError("""Incorrect data format, should be:
                            '%Y-%m-%d %H:%M:%S ;Reader [event]; E/[]/KD1/[]-[]
                            """)
    except FileNotFoundError:
        raise FileNotFoundError(" Could not open file 'input.csv' ")

    next(input_read)        #pomija naglowek
    


    input_list = list(input_read)   # utworzenie listy elementow

validation_of_rows(input_list)  # sprawdzenie poprawnosci wpisanych danych



_date  = 0   # zmienne odpowiadajace wartosciom w liscie
event = 1    # zebranej z pliku "input.csv"
gate  = 2 


dict_of_days = dict()


# stworzenie slownika dni i w nim kolejnego slownika z godzinami wejscia/wyjsca
# i wpisanie godzin wyjsca wejsca pogrupowane dniami
for index in range(len(input_list)):

    formated_day = datetime.strptime( input_list[index][_date], "%Y-%m-%d %H:%M:%S " )

    formated_date = formated_day.date()
    
    if formated_date not in dict_of_days.keys():
        dict_of_days[formated_date] = { 
            'batches_of_time_in':{},
            'sum_of_work': int(),
            'flags':{
                'weekend':"",
                'overtime':"", 
                'undertime':"", 
                'inconclusive':"",
                },
            'out_of_office':1
        }
    

    # z rozpatrywanej daty wybierany jest tylko czas w postaci "hh:mm:ss"
    formated_time = formated_day.time()
    
    # zmienne sprawdzajace poprawnosc wproawdzanch godzin
    # (aby zapobiedz mozliwosci wprowadzenia godziny wczesniejszych
    #  niz zapisane poprzedni) sa zerowane
    fr_td = 0   #formated_time_timedelta - obiekt timedelta rozpatrywanego czasu
    ls_td = 0   #last_timedelta - obiekt timedelta ostatnio rozpatywanego czasu


    # numer pietra na ktorym znajduje sie bramka 
    floor_number = input_list[index][gate][2] 

    # podpisane indeksy w liscie skladajacej sie z [czasu_wejscia, czasu_wyjscia] (z biura)
    _entry = 0
    _exit = 1

    # test czy nastepna godzina tego samego dnia nie jest "wczesniejsza"
    # od poprzednich
    try:
        is_this_correct_time(formated_day, ls)
    except NameError:
        pass
    
    # 
    ls = formated_day
    
    #jesli jest to godzina WEJSCIA
    if "entry" in input_list[index][event]:

        #jesli nie ma jeszcze daty na liscie
        if dict_of_days[formated_date]['batches_of_time_in'] == {}:
            # zmienna oznaczajaca "partie" czasu spedzonego w biurze
            # zaczynamy od 1 partii, jesli wyjdzie z biura, zwiekszamy
            # ja o jeden
            batch = 1
            dict_of_days[formated_date]['batches_of_time_in'][batch] = list()
        
        if batch in list(dict_of_days[formated_date]['batches_of_time_in'].keys()):
            
            # dodaj ja jako pierwsza
            if dict_of_days[formated_date]['batches_of_time_in'][batch] == list():

                dict_of_days[formated_date]['batches_of_time_in'][batch].append(formated_time)
                dict_of_days[formated_date]['batches_of_time_in'][batch].append(formated_time)

                # flaga na 0 - czyli jest w biurze
                dict_of_days[formated_date]['out_of_office'] = 0


            # na miejsce czasu WYJŚCIA tymczasowo zapisywany jest 
            # ostatni czas WEJŚCIA, gdyby nie znaleziono jakiegos
            # czasu wyjscia to ten zostanie za niego uznany
            else: 
                # ustatawiamy flage 'inconclusive'
                dict_of_days[formated_date]['flags']['inconclusive'] = "i "
                dict_of_days[formated_date]['batches_of_time_in'][batch][_exit] = formated_time
       
        # utworzenie nowej parti godzin spedzonych w biurze
        else:

            dict_of_days[formated_date]['batches_of_time_in'][batch] = list()
            
            dict_of_days[formated_date]['batches_of_time_in'][batch].append(formated_time)
            dict_of_days[formated_date]['batches_of_time_in'][batch].append(formated_time)

            # flaga na 0 - czyli jest w biurze
            dict_of_days[formated_date]['out_of_office'] = 0
    

    # jesli jest to godzina WYJSCIA
    elif "exit" in input_list[index][event]:
        # jesli ta partia czasu znajduje sie w wartosciach
        if batch in list(dict_of_days[formated_date]['batches_of_time_in'].keys()):
            # jesli lista godzin tej partii nie jest pusta, czyli juz wszedl
            if len(dict_of_days[formated_date]['batches_of_time_in'][batch]) != 0:
                # jesli na miejscu godziny wejscia jest odpowiedni typ <datatime.time>
                if type(dict_of_days[formated_date]['batches_of_time_in'][batch][_entry]) == type(formated_time):

                    
                    # jesli przechodzi przez bramke na parterze
                    if floor_number == str(0):
                        # jesli znajduje sie w biurze
                        if dict_of_days[formated_date]['out_of_office'] == 0:
                            
                            # dodaj pierwsza godzine WYJSCIA 
                            dict_of_days[formated_date]['batches_of_time_in'][batch][1] = formated_time

                            # po tym wyjsciu z biura, jesli do niego wroci
                            # utworzymy kolejna partie czasu
                            batch += 1

                            # wyszedl z biura wiec ustawiamy flage na 1
                            dict_of_days[formated_date]["out_of_office"] = 1

                            # znaleziono czasy wyjscia wiec mozemy usunac flage
                            # jest to konieczne poniewaz w warunku wyzej profilaktycznie
                            # ja ustawiamy na wypadek gdyby nie byl podany zaden z 
                            # czasow WYJSCIA
                            dict_of_days[formated_date]['flags']['inconclusive'] = ""

                
        
            else:
                dict_of_days[formated_date]['flags']['inconclusive'] = "i "
                #raise ValueError("Nie mozesz wyjsc jak jeszcze nie weszles")
            
        # jesli nie byloby godziny WEJSCIA tego dnia, ale byly WYJSCIA
        else:
            # ustaw flage 'inconclusive'
            dict_of_days[formated_date]['flags']['inconclusive'] = "i "
            batch = 1
            #stworz nowa liste ktora bedzie przechowywala [czas_rozpoczacia, czas_zakonczenia]
            dict_of_days[formated_date]['batches_of_time_in'][batch] = list()
            
            # wypelnij liste najpierw godzina WEJSCIA rowna 00:00:00
            dict_of_days[formated_date]['batches_of_time_in'][batch].append(time(second=0))
            # i index 1 faktyczna godzina WYJSCIA 
            dict_of_days[formated_date]['batches_of_time_in'][batch].append(formated_time)

            # flaga na 1 - czyli jest poza biurem
            dict_of_days[formated_date]['out_of_office'] = 1



# oblicza czas pracy konkretnego dnia
for day in dict_of_days.values():
    get_sum_of_time(day)


with open('result', 'w') as result:
    # wypisywanie ostatecznego komunikatu
    for day in dict_of_days:


        # suma pracy calego dnia przekonwertowana z 'timedelta' do formatu: hours:min:sec
        time_of_work = timedelta_to_HMS(dict_of_days[day]['sum_of_work'])


        #-----Flagi----
        weekly_time_of_work = ""        # puste zmienne-flagi ktore beda wypelnione
        normal_time_of_work = ""        # odpowiednimi wartosciami jesli 
        time_over = ""                  # spelnia warunki 
        time_under = ""
        

        if (day.weekday() == 5 or day.weekday() == 6):      # jesli dany dzien byl  
            dict_of_days[day]['flags']['weekend'] = "w "     # weekendem - dodaj flage 'w'
        
        if ( dict_of_days[day]['sum_of_work'] > timedelta(hours=9) ):   # jesli przepracowal ponad 9h 
            dict_of_days[day]['flags']['overtime'] = "ot "               # dodaj flage 'ot'
        
        if ( dict_of_days[day]['sum_of_work'] < timedelta(hours=6) ):   # jesli przepracowal mniej niz
            dict_of_days[day]['flags']['undertime'] = "ut "              # 6h - dodaj flage 'ut'
        
        # Przypisanie odpowiednich wartosci flagom
        weekend = dict_of_days[day]['flags']['weekend']
        overtime = dict_of_days[day]['flags']['overtime']
        undertime = dict_of_days[day]['flags']['undertime']
        inconclusive = dict_of_days[day]['flags']['inconclusive']

        
        # Utworzenie slownika z ostantimi dniami tygodnia za pomoca funkcji
        dict_of_last_days = get_last_days(dict_of_days)

        
        # jesli dzien jest ostatnim dniem tygodnia to zlicz caly przepracowany w nim czas
        if day in dict_of_last_days.values():
            weekly_time_of_work, normal_time_of_work = get_weekly_time_of_work(dict_of_days, dict_of_last_days, day)
            
            
            # obliczenie ilosci czasu nadgodzin i niewyrobienia normy przez caly tydzien
            
            time_1 = weekly_time_of_work        # czas przepracowany

            time_2 = timedelta(hours=normal_time_of_work)   # ktory powinien byc przepracowany

            if(time_1 == time_2):   # jesli nie przepracowano przepracowano         
                pass                # co do sekundydokladnie tyle ile powinno
                                                        
            # jesli nie przepracowan nawet sekundy (np. blad systemu)
            elif time_1.seconds == 0:
                time_under = timedelta_to_HMS(time_2)   # konwersja na string do wypisania w
                time_under = f"-{time_under}"           # wymaganym formacie i dodatnie "-"
                

            # jesli sa wyrobione nadgodziny                            
            elif time_1 > time_2:               
                time_over = time_1 - time_2
                time_over = timedelta_to_HMS(time_over) # konwersja na string do wypisania w
                                                        # wymaganym formacie

            # jesli nie wyrobiono normy
            elif time_1 < time_2:               
                time_under = time_2 - time_1
                time_under = timedelta_to_HMS(time_under) # konwersja na string do wypisania w
                time_under = f"-{time_under}"             # wymaganym formacie i dodatnie "-"
                
    

            # konwersja z timedelta na string w odpowiednim formacie (bez dni, >24h)
            weekly_time_of_work = timedelta_to_HMS(weekly_time_of_work)


        
        


        print(f"Day {day} Work {time_of_work} {weekend}{overtime}{undertime}{inconclusive} {weekly_time_of_work} {time_under}{time_over}")

        result.write(f"Day {day} Work {time_of_work} {weekend}{overtime}{undertime}{inconclusive} {weekly_time_of_work} {time_under}{time_over}\n")




    
        
     