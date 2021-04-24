from pprint import pprint
import csv
from datetime import datetime, timedelta, date, time
import re 

        #testy :
        #- sprawdzic z ujemna data
        #- sprawdzic z jakimis zlymi danymi, zrobic validacje tego wszystkiego
        #   np. pusty wiersz
        #       niepoprawny format: daty, eventu, bramki
        #


# ------------------------- To dziala ------------------------------------

def validation_of_rows(input_list):

    i_date = 0
    i_event = 1
    i_gate  = 2

    for row in input_list:

        if row == []:       # jesli mamy pusty wiersz to go usun
            input_list.remove(row)
        
        else:

            # format daty
            #pattern_date = re.compile(r'[0-2][0-9]{3}-[0-1][0-9]-[0-3][')
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


        


#   DZIALAJACA WERSJA NA KULCZACH-TYGODNIACH, WARTOSCIACH-DNIACH

def get_last_days(dict_of_days):

    # funkcja obliczajaca ktore dni w podanych danych sa ostatnimi dniami danego
    # tygodnia, dostaje wczesniej utworzony slownik ze wszystkimi podanymi na 
    # wejsciu przepracowanymi dniami i zwraca kolejny slownik tylko ostatnich
    # dni tygodnia

    list_of_last_days = dict()  # tworzymy nowy slownik

    last_day = list(dict_of_days.keys())[0] # zapisujemy w zmiennej pierwszy
                                            # rozpatrywany dzien

    week_of_last_day = last_day.isocalendar()[1]

    list_of_last_days[week_of_last_day] = last_day

    for day in dict_of_days:

        week_of_last_day = last_day.isocalendar()[1] #zwraca tydzien w ktotrym znajduje sie ten dzien
        week_of_this_day = day.isocalendar()[1]      #to samo tylko dla rozpatrywanego dnia

        # jesli rok jest ten sam
        if day.year == last_day.year:
                #jesli tydzien jest ten dam
            if  week_of_last_day ==  week_of_this_day:
                    #numer dnia w tygodniu danego dnia jest wiekszy od "ostatniego", np: czwartek > wtorku
                if day.weekday() >= list_of_last_days[week_of_last_day].weekday():
                    # zamien ostatni dzien na aktualnie rozpatrywany pod tym kluczem 
                    list_of_last_days[week_of_last_day] = day
                    # i zmienna last_day ustaw na rozpatrywany dzien
                    last_day = day
            else:
                #jesli sa z roznych tygodni to stworz nowy klucz z tym dniem
                list_of_last_days[week_of_this_day] = day
                # i przypisz do zmiennej last_day
                last_day = day
        else:
            #jesli sa z roznych lat to stworz nowy klucz z tym dniem
            list_of_last_days[week_of_this_day] = day
            # i przypisz do zmiennej last_day
            last_day = day


    return list_of_last_days


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

            else:
                pass

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

    date_format = "%Y-%m-%d %H:%M:%S " # format zczytywanej z pliku daty
    

    dict_of_days = dict()


    # stworzenie slownika dni i w nim kolejnego slownika z godzinami wejscia/wyjsca
    # i wpisanie godzin wyjsca wejsca pogrupowane dniami
    for index in range(len(input_list)):

        formated_date = datetime.strptime( input_list[index][_date], date_format ).date()
        
        if formated_date not in dict_of_days.keys():
            dict_of_days[formated_date] = { 
                'entry_hours':list(),
                'exit_hours':list(),
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
        formated_time = datetime.strptime( input_list[index][_date], date_format ).time()
        
        # zmienne sprawdzajace poprawnosc wproawdzanch godzin
        # (aby zapobiedz mozliwosci wprowadzenia godziny wczesniejszych
        #  niz zapisane poprzedni) sa zerowane
        fr_td = 0   #formated_time_timedelta - obiekt timedelta rozpatrywanego czasu
        ls_td = 0   #last_timedelta - obiekt timedelta ostatnio rozpatywanego czasu
        
        # numer pietra na ktorym znajduje sie bramka 
        floor_number = input_list[index][gate][2] 

        if "entry" in input_list[index][event]:

            if len(dict_of_days[formated_date]['exit_hours']) == 0:
                pass

            #jesli nie ma jeszcze daty na liscie
            if len(dict_of_days[formated_date]['entry_hours']) == 0:
                # dodaj ja jako pierwsza
                dict_of_days[formated_date]['entry_hours'].append(formated_time)
                # ustaw ja jako ostatnia rozpatrywana date
                ls = formated_time  # ls - ostatnia rozpatrywana data

                dict_of_days[formated_date]['out_of_office'] = 0

            # konwersja na typ timedela aby moc porownac aktualnie 
            # rozpatrywana godzine z ostantio rozpatrywana godzine
            # aby wykryc ewentualne bledy z godzinami
             
            # formated_time_timedelta
            fr_td = timedelta(hours=formated_time.hour, minutes=formated_time.minute, seconds= formated_time.second)
            # last_timedelta
            ls_td = timedelta(hours=ls.hour, minutes=ls.minute, seconds= ls.second)

            # jesli dodatwana godzina jest "pozniejsza" od poprzedniej
            # to wszystko w porzadku
            if fr_td > ls_td:
                # dodaj ja jako kolejna godzine
                dict_of_days[formated_date]['entry_hours'].append(formated_time)
                # ustaw ja jako ostantio dodana
                ls = formated_time

            # jesli nie to pomin jak i ustaw flage "inconclusive"
            elif fr_td < ls_td:
                dict_of_days[formated_date]['flags']['inconclusive'] = "i "
                
                # raise ValueError(f"Entry time of day {formated_date} - {fr_td} is earlier than the previous one : {ls_td}")

        

        elif "exit" in input_list[index][event]:
            
            # jesli lista godzin wyjscia jest pusta
            if len(dict_of_days[formated_date]['exit_hours']) == 0:
                # dodaj pierwszy element
                dict_of_days[formated_date]['exit_hours'].append(formated_time)

                # jesli przechodzi przez bramke na parterze
                if floor_number == 0:
                    dict_of_days[formated_date]["out_of_office"] = 1
                

                ls = formated_time  # ls - ostatnia rozpatrywana data

            # konwersja na typ timedela aby moc porownac aktualnie 
            # rozpatrywana godzine z ostantio rozpatrywana godzine
            # aby wykryc ewentualne bledy z godzinami
             
            # formated_date_timedelta
            fr_td = timedelta(hours=formated_time.hour, minutes=formated_time.minute, seconds= formated_time.second)
            # last_day_timedelta
            ls_td = timedelta(hours=ls.hour, minutes=ls.minute, seconds= ls.second)

            # eliminujemy mozliwosc podania wczesniejszej godziny WYJSCIA
            # z biorua niz godzina WEJSCIA do biura

            # zapisujemy w "entry_hour" kazda godzine ktora zostala
            # do tej pory zarejestrowana jako poprawna godzina wejscia
            for entry_hour in dict_of_days[formated_date]['entry_hours']:

                # tworzymy obiekt timedelta ktora pozwoli nam porownywac czas
                # ls_e_td - last_entry_timedelta
                ls_e_td = timedelta(hours=entry_hour.hour, minutes=entry_hour.minute, seconds= entry_hour.second)
                


                # # jesli rozpatrywana godzina WYJSCIA jest "mniejsza" niz jakas 
                # # wczesniej zarejestrowana godzina WEJSCIA
                # if fr_td < ls_e_td:
                #     raise ValueError(f"Dnia {formated_date}, wszedl: {ls_e_td}, a wychodzi: {fr_td}")

            # jesli dodatwana godzina jest "pozniejsza" od poprzedniej
            # to wszystko w porzadku
            if fr_td > ls_td:
                # dodaj ja jako kolejna godzine
                dict_of_days[formated_date]['exit_hours'].append(formated_time)
                # ustaw ja jako ostantio dodana
                ls = formated_time

            # jesli nie to pomin i ustaw flage "inconclusive"
            elif fr_td < ls_td:
                dict_of_days[formated_date]['flags']['inconclusive'] = "i "
                
                # raise ValueError(f"Exit time of day {formated_date} - {fr_td} is earlier than the previous one : {ls_td}")

            
            #print(f"formated_time: {fr_td}, last_date: {ls_td}")
        print(f"formated_time: {formated_date}")
        print(f"left the office: {dict_of_days[formated_date]['out_of_office']}")
        



    # oblicza czas pracy tego dnia
    for day in dict_of_days:
        tmp_date = date(1, 1, 1)

        if ( len(dict_of_days[day]['entry_hours']) == 0 ):
            dict_of_days[day]['flags']['inconclusive'] = "i "

            start_work = datetime.combine(tmp_date, dict_of_days[day]['exit_hours'][0])
            end_work = datetime.combine(tmp_date, dict_of_days[day]['exit_hours'][-1])
            suma = end_work - start_work 
            

            dict_of_days[day]['sum_of_work'] =  timedelta(seconds = suma.seconds)

        elif (len(dict_of_days[day]['exit_hours']) == 0 ):
            dict_of_days[day]['flags']['inconclusive'] = "i "

            start_work = datetime.combine(tmp_date, dict_of_days[day]['entry_hours'][0])
            end_work = datetime.combine(tmp_date, dict_of_days[day]['entry_hours'][-1])
            suma = end_work - start_work 

            dict_of_days[day]['sum_of_work'] =  timedelta(seconds = suma.seconds)
        
        else:
            
            start_work = datetime.combine(tmp_date, dict_of_days[day]['entry_hours'][0])
            end_work = datetime.combine(tmp_date, dict_of_days[day]['exit_hours'][-1])
            suma = end_work - start_work 


            dict_of_days[day]['sum_of_work'] =  timedelta(seconds = suma.seconds)

    

    with open('result', 'w') as result:
        # wypisywanie ostatecznego komunikatu
        for day in dict_of_days:
            #time_of_work = str(dict_of_days[day]['sum_of_work'])

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

                if(time_1 == time_2):   # jesli nie przepracowano nawet sekundy
                    pass                                       # choc dni sa wpisane (np. blad systemu)
                                                                # lub przepracowano co do sekundy        
                                                                # dokladnie tyle ile powinno 

                elif time_1.seconds == 0:
                    
                    time_under = timedelta_to_HMS(time_2)
                    #print(f"time_2: {time_2} -{time_under} ")
                    time_under = f"-{time_under}"

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
                    
                

                
            

                # zmiana dni na godziny bo timedelta wypisze w formie np. 1 day 22:11:00
                weekly_time_of_work = timedelta_to_HMS(weekly_time_of_work)


            
            


            print(f"Day {day} Work {time_of_work} {weekend}{overtime}{undertime}{inconclusive} {weekly_time_of_work} {time_under}{time_over}")

            result.write(f"Day {day} Work {time_of_work} {weekend}{overtime}{undertime}{inconclusive} {weekly_time_of_work} {time_under}{time_over}\n")

# ------------------------- To dziala ------------------------------------


 

            # jesli w GATE poziom 0 (E/0/*)
            # to znaczy ze wyszedl z pracy
            # reszta bram to nadal bramy
            # w pracy


    
        
          # plik wyjsciowy 