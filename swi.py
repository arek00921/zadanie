from pprint import pprint
import csv
from datetime import datetime, timedelta, date, time
import re 

class BatchOfWork:

    """
        klasa dla obiektu kontrolujacego ilosc "parti"
        czasu spedzonego w biurze
    """

    def __init__(self, value=1):
        self.value = value

    def increment(self):
        self.value += 1
    
    def decrement(self):
        self.value -= 1

    def set_value(self, value=1):
        self.value = value

    def get_value(self):
        return self.value

def read_rows_from_input():

    '''
    funkcja probuje otworzyc plik input.csv,
    sprawdza czy istnieje, czy nie jest pusty
    i zwraca wiersze w postaci listy bez naglowka 
    '''

    with open('input.csv', 'r') as input_file:
        
        try:
            input_read = csv.reader(input_file, delimiter=';')
        except ValueError:
            raise ValueError("""Incorrect data format, should be:
                                '%Y-%m-%d %H:%M:%S ;Reader [event]; E/[]/KD1/[]-[]
                                """)
        except FileNotFoundError:
            raise FileNotFoundError(" Could not open file 'input.csv' ")

        input_list = list(input_read)

        # jesli plik nie jest pusty
        if (len(input_list) == 0):
            raise ValueError("Input file is empty!")
        
        return input_list[1:]


def validation_of_rows(input_list):

    ''' 
    funkcja sprawdzajaca poprawnosc wpisanych danych
    jesli ktorys z wierzy nie bedzie pasowal do okreslonego
    formatu, funkcja zwroci blad
    '''

    I_DATE = 0
    I_EVENT = 1
    I_GATE  = 2

    for row in input_list:

        # jesli mamy pusty wiersz to go usun
        if row == []:               
            input_list.remove(row)
        else:

            # format daty
            try:
                datetime.strptime(row[I_DATE], '%Y-%m-%d %H:%M:%S ')
            except ValueError as err:
                print(err)

            # format eventu
            pattern_event = re.compile(r'Reader (exit|entry)')
            matched_event = re.match(pattern_event, row[I_EVENT])
            is_matched_event = bool(matched_event)

            if is_matched_event is False:
                raise ValueError(f'Event data does not match format: Reader (exit|entry)')

            #format bramki
            pattern_gate = re.compile(r'^E/[0-3]/KD1/[0-9]-[0-9]$')
            matched_gate = re.match( pattern_gate, row[I_GATE])
            is_matched_gate = bool(matched_gate)

            if is_matched_gate is False:
                raise ValueError(f'Data Gate does not match format: E/[0-3]/KD1/[0-9]-[0-9]')

def get_formated_date(str_date):

    ''' 
    funkcja przyjmuje date jako string w 
    formacie YYYY-MM-DD hh:mm:ss i zwraca
    ja jako obiekt datetime.datetime
    '''

    return datetime.strptime(str_date, "%Y-%m-%d %H:%M:%S ")

def make_dict_of_days(input_list):

    '''
    funkcja tworzy slownik w ktorych kluczami
    sa daty zczytane z pliku
    '''

    dict_of_days = dict()


    for index in range(len(input_list)):

        batch_obj = BatchOfWork()


        formated_day = get_formated_date(input_list[index][DATE])

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
                'out_of_office':1,
                'batch_obj':batch_obj
            }

    return dict_of_days

def is_this_correct_time(now, before):

    '''
    funkcja sprawdza poprawnosc wprowadzonych godzin
    w pliku wejsciowym, jesli rozpatrywana godzina
    bedzie "mniejsza" niz poprzednia tego samego dnia
    ustawi flage 'inconclusive'
    '''

    # konwersja na typ timedela aby moc porownac aktualnie 
    # rozpatrywana godzine z ostantio rozpatrywana godzine
    # aby wykryc ewentualne bledy z godzinami

    # czy sa to te same dni
    if now.date() == before.date():
        formated_time = now.time()
        ls = before.time()

        # formated_time_timedelta
        fr_td = timedelta(hours=formated_time.hour, minutes=formated_time.minute, seconds= formated_time.second)
        # last_timedelta
        ls_td = timedelta(hours=ls.hour, minutes=ls.minute, seconds= ls.second)

        # jesli nie to ustaw flage "inconclusive"
        if fr_td < ls_td:
            dict_of_days[formated_date]['flags']['inconclusive'] = "i "
            raise ValueError(f"Time of day {now} - {fr_td} is earlier than the previous one : {ls_td}")

def add_entry_hour(dict_of_days, formated_day):

        '''
        funkcja dodaje do konkretnego dnia
        godzine wejsca do biura
        '''
        
        # ograniczenie daty tylko do YYYY-MM-DD
        formated_date = formated_day.date()
        
        # ograniczenie daty tylko do hh:mm:ss
        formated_time = formated_day.time()

        # indywidualny numer "partii" kazdego dnia
        batch_obj = dict_of_days[formated_date]['batch_obj']
        batch_value = batch_obj.get_value()


        #jesli nie ma jeszcze daty na liscie
        if dict_of_days[formated_date]['batches_of_time_in'] == {}:
            # obiekt ktorego wartosc oznacza "partie" czasu spedzonego 
            # w biurze zaczynamy od 1 partii, jesli wyjdzie z biura, 
            # zwiekszamy ja o jeden
            batch_obj.set_value(1)
            dict_of_days[formated_date]['batches_of_time_in'][batch_value] = list()
        
        if batch_value in list(dict_of_days[formated_date]['batches_of_time_in'].keys()):
            
            # dodaj ja jako pierwsza
            if dict_of_days[formated_date]['batches_of_time_in'][batch_value] == list():
                

                dict_of_days[formated_date]['batches_of_time_in'][batch_value].append(formated_time)
                dict_of_days[formated_date]['batches_of_time_in'][batch_value].append(formated_time)

                # flaga na 0 - czyli jest w biurze
                dict_of_days[formated_date]['out_of_office'] = 0


            # na miejsce czasu WYJŚCIA tymczasowo zapisywany jest 
            # ostatni czas WEJŚCIA, gdyby nie znaleziono zadnego 
            # innego czasu wyjscia to ten zostanie za niego uznany
            else: 
                # ustatawiamy flage 'inconclusive'
                dict_of_days[formated_date]['flags']['inconclusive'] = "i "
                dict_of_days[formated_date]['batches_of_time_in'][batch_value][EXIT] = formated_time
       
        # utworzenie nowej parti godzin spedzonych w biurze
        else:

            dict_of_days[formated_date]['batches_of_time_in'][batch_value] = list()
            
            dict_of_days[formated_date]['batches_of_time_in'][batch_value].append(formated_time)
            dict_of_days[formated_date]['batches_of_time_in'][batch_value].append(formated_time)

            # flaga na 0 - czyli jest w biurze
            dict_of_days[formated_date]['out_of_office'] = 0

def add_exit_hour(dict_of_days, formated_day, floor_number):

    '''
    funkcja dodaje do konkretnego dnia
    godzine wyjscia z biura
    '''        

    # ograniczenie daty tylko do YYYY-MM-DD
    formated_date = formated_day.date()
        
    # ograniczenie daty tylko do hh:mm:ss
    formated_time = formated_day.time()

    # indywidualny numer "partii" kazdego dnia
    batch_obj = dict_of_days[formated_date]['batch_obj']
    batch_value = batch_obj.get_value()


    # jesli ta partia czasu znajduje sie w wartosciach
    if batch_value in list(dict_of_days[formated_date]['batches_of_time_in'].keys()):
        # jesli lista godzin tej partii nie jest pusta, czyli juz wszedl
        if len(dict_of_days[formated_date]['batches_of_time_in'][batch_value]) != 0:
            # jesli na miejscu godziny wejscia jest odpowiedni typ <datatime.time>
            if type(dict_of_days[formated_date]['batches_of_time_in'][batch_value][ENTRY]) == type(formated_time):

                
                # jesli przechodzi przez bramke na parterze
                if floor_number == str(0):
                    # jesli znajduje sie w biurze
                    if dict_of_days[formated_date]['out_of_office'] == 0:
                        
                        # dodaj pierwsza godzine WYJSCIA 
                        dict_of_days[formated_date]['batches_of_time_in'][batch_value][1] = formated_time

                        # po tym wyjsciu z biura, jesli do niego wroci
                        # utworzymy kolejna partie czasu
                        batch_obj.increment()

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

        batch_obj.set_value(1)

        #stworz nowa liste ktora bedzie przechowywala [czas_rozpoczacia, czas_zakonczenia]
        dict_of_days[formated_date]['batches_of_time_in'][batch_value] = list()
        
        # wypelnij liste najpierw godzina WEJSCIA rowna 00:00:00
        dict_of_days[formated_date]['batches_of_time_in'][batch_value].append(time(second=0))
        # i index 1 faktyczna godzina WYJSCIA 
        dict_of_days[formated_date]['batches_of_time_in'][batch_value].append(formated_time)

        # flaga na 1 - czyli jest poza biurem
        dict_of_days[formated_date]['out_of_office'] = 1


def fill_day_with_worktime(input_list):

    '''
    funkcja wypelnienia kazdy dzien odpowiednimi partiami
    zawierajacymi czas wjescia do biura i wyjscia z niego
    '''

    for row in input_list:

        # konwersja daty z str na datetime.datetime
        formated_day = get_formated_date(row[DATE])

        # test czy nastepna godzina tego samego dnia nie jest "wczesniejsza"
        # od poprzednich
        try:
            is_this_correct_time(formated_day, last_day)
        except NameError:
            pass
        
        last_day = formated_day
        

        #jesli jest to godzina WEJSCIA
        if "entry" in row[EVENT]:
            add_entry_hour(dict_of_days, formated_day)


        # jesli jest to godzina WYJSCIA
        elif "exit" in row[EVENT]:

            # numer pietra na ktorym znajduje sie bramka 
            floor_number = row[GATE][2] 
            add_exit_hour(dict_of_days, formated_day, floor_number)


def substract_datetime(start, end):

    '''
    funkcja odejmujaca od siebie dwie podane godziny,
    zwraca obiekt timedelta
    '''

    tmp_date = date(1,1,1)
    start = datetime.combine( tmp_date, start )
    end = datetime.combine( tmp_date, end )

    return end - start

def get_sum_of_time(day):

    '''
    funkcja przypisuje atrybutowi 'sum_of_work'- rozpatrywanego
    dnia w slowniku dict_of_days - sume calego czasu 
    spedzonego w biurze 
    '''

    # zmienna odpowiedzialna za przechowanie sumy czasu
    # wszystkich partii pracy
    sum_of_all_batch = timedelta(seconds=0)
    
    # ilosc "partii" w ktorych przebywal w biurze
    number_of_batches = len(list(day['batches_of_time_in'].keys()))


    # jesli tego dnia nie przebywal w biurze 
    if number_of_batches == 0:
        day['flags']['inconclusive'] = "i "
        day['sum_of_work'] =  timedelta(seconds = 0)

    # jesli tego dnia przebywal w biurze
    else:
        # wykonaj dla kazdej parti pracy
        for index in range(1,number_of_batches+1):
            
            # przypisujemy do zmiennych konkretne godzinowe wartosci wejscia
            # i wyjscia do/z budynku
            start_work = day['batches_of_time_in'][index][ENTRY]
            end_work = day['batches_of_time_in'][index][EXIT]
                
            # suma jednej partii
            sum_of_one_batch = substract_datetime(start_work, end_work)
            sum_of_all_batch += sum_of_one_batch

        # zapisujemy w slowniku konkretnego dnia ilosc czasu spedzonego w biurze
        day['sum_of_work'] =  timedelta(seconds = sum_of_all_batch.seconds)


def get_last_days(dict_of_days):

    '''
    funkcja obliczajaca ktore dni w podanych danych 
    sa ostatnimi dniami danego tygodnia 
    '''

    # Keys: tydzien, Values: ostatni przepracowany 
    #                        dzien w tym tygodniu
    dict_of_last_days = dict() 

    # zapisujemy w zmiennej pierwszy rozpatrywany dzien
    last_day = list(dict_of_days.keys())[0] 

    # zapisujemy numer tygodnia w skali rocznej tego dnia
    week_of_last_day = last_day.isocalendar()[1]

    dict_of_last_days[week_of_last_day] = last_day

    for day in dict_of_days:

        # tydzien w ktorym znajduje sie ostatnio rozpatrywany dzien
        week_of_last_day = last_day.isocalendar()[1] 
        # tydzien w ktorym znajduje sie akutalnie rozpatrywany dzien
        week_of_this_day = day.isocalendar()[1]      

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

    '''
    funkcja obliczajaca ilosc przepracowanego czasu w calym tygodniu od dnia podanego
    w 'day', ze wszystkich podanych mu dni zapisanych w pierwszym podawanym slowniku
    zliczy przepracowany czas od poczatku danego tygodnia pracy (niekoniecznie
    poniedzialku, dowolnie) do konca (rowniez dowolnie)
    '''
  
    counter_of_working_days = 0             

    # zmienna przechowujaca przepracowany 
    # czas w sekundach ustawiona na zero
    weekly_time_of_work = timedelta(seconds=0)  
    
    # zmienna wskazuje od jakiego dnia tygodnia 
    # zaczynamy sprawdzac ilosc dni
    days_to_first_working_day = day.weekday()       
    
    # "iterator" po dniach tygodnia
    next_day = timedelta(days=1)

    # rozpatrywany dzien, ustawiony na 
    week_day = day - timedelta(days=days_to_first_working_day)   

    while week_day != (day+next_day):
        
        if week_day in dict_of_days.keys():

            # zmienna przechowuje ilosc pracy 
            # danego dnia w sekndach
            sum_of_work = dict_of_days[week_day]['sum_of_work']  
            
            weekly_time_of_work += sum_of_work 

            counter_of_working_days += 1

        week_day = week_day + next_day 

    normal_time_of_work = 8 * counter_of_working_days
    
    return weekly_time_of_work, normal_time_of_work

def timedelta_to_HMS(time_delta_data):

    '''
    funkcja konwertujaca obiekt 'timedelta' (ktory automatycznie wyswiela
    podany czas w optymalnej postaci, tj. jesli jest wiecej niz 24h to
    zaczyna dopisywac dni) w zmienne odpowiadajace konkretnym danym
    czasowym ktore sa umieszczane w formie zwyklego stringa
    ''' 

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
        
    # wymuszamy format zawsze dwoch cyfr (00:00:00 zamiast 0:0:0)
    f_HMS = f"{w_hours:02}:{w_min:02}:{w_sec:02}"


    return f_HMS

def setting_flags(dict_of_days, day):

    '''
    funkcja ustawia odpowiednie flagi
    '''

    if (day.weekday() == 5 or day.weekday() == 6):      # jesli dany dzien byl  
            dict_of_days[day]['flags']['weekend'] = "w "     # weekendem - dodaj flage 'w'
    
    if ( dict_of_days[day]['sum_of_work'] > timedelta(hours=9) ):   # jesli przepracowal ponad 9h 
        dict_of_days[day]['flags']['overtime'] = "ot "               # dodaj flage 'ot'
    
    if ( dict_of_days[day]['sum_of_work'] < timedelta(hours=6) ):   # jesli przepracowal mniej niz
        dict_of_days[day]['flags']['undertime'] = "ut "              # 6h - dodaj flage 'ut'



def calculate_under_over_time(weekly_time_of_work, normal_time_of_work,time_under_over):
 
    '''
    funkcja oblicza ilosci czasu 
    nadgodzin/niewyrobienia normy 
    przez caly tydzien
    '''

    time_1 = weekly_time_of_work        # czas przepracowany

    time_2 = timedelta(hours=normal_time_of_work)   # czas ktory powinien byc przepracowany

    if(time_1 == time_2):   # jesli nie przepracowano przepracowano         
        pass                # co do sekundydokladnie tyle ile powinno
                                                
    # jesli nie przepracowan nawet sekundy (np. blad systemu)
    elif time_1.seconds == 0:
        time_under_over = timedelta_to_HMS(time_2)
        time_under_over = f"-{time_under_over}"


    # jesli sa wyrobione nadgodziny                            
    elif time_1 > time_2:               
        time_under_over = time_1 - time_2
        time_under_over = timedelta_to_HMS(time_under_over)

    # jesli nie wyrobiono normy
    elif time_1 < time_2:               
        time_under_over = time_2 - time_1
        time_under_over = timedelta_to_HMS(time_under_over)
        
    return time_under_over


def write_data_to_result(dict_of_days):

    '''
    funkcja otwiera/tworzy plik "result"
    i zapisuje w nim wszystkie obliczone 
    dane wraz z flagami
    '''
    
    with open('result', 'w') as result:
        for day in dict_of_days:

            # suma pracy calego dnia przekonwertowana z 'timedelta' do formatu: hours:min:sec
            time_of_work = timedelta_to_HMS(dict_of_days[day]['sum_of_work'])

            # Ustawienie odpowiednich wartosci flagom
            setting_flags(dict_of_days, day)    

            # Przypisanie odpowiednich wartosci flagom
            weekend = dict_of_days[day]['flags']['weekend']
            overtime = dict_of_days[day]['flags']['overtime']
            undertime = dict_of_days[day]['flags']['undertime']
            inconclusive = dict_of_days[day]['flags']['inconclusive']


            #-----Flagi----
            weekly_time_of_work = ""        # puste zmienne-flagi ktore beda wypelnione
            normal_time_of_work = ""        # odpowiednimi wartosciami jesli 
            time_under_over = ""            # spelnia warunki 
            
            # Utworzenie slownika z ostantimi dniami tygodnia za pomoca funkcji
            dict_of_last_days = get_last_days(dict_of_days)

            
            # jesli dzien jest ostatnim dniem tygodnia to zlicz caly przepracowany w nim czas
            if day in dict_of_last_days.values():
                
                # obliczenie tygodniowego czasu pracy i ilosci godzin ktore powinien przepracowac
                weekly_time_of_work, normal_time_of_work = get_weekly_time_of_work(dict_of_days, dict_of_last_days, day)
                
                # obliczenie czasu nadgodzin/niewyrobienia normy
                time_under_over = calculate_under_over_time(weekly_time_of_work, normal_time_of_work, time_under_over)

                # konwersja z timedelta na string w odpowiednim formacie (bez dni, >24h)
                weekly_time_of_work = timedelta_to_HMS(weekly_time_of_work)

            print(f"Day {day} Work {time_of_work} {weekend}{overtime}{undertime}{inconclusive} {weekly_time_of_work} {time_under_over}")

            result.write(f"Day {day} Work {time_of_work} {weekend}{overtime}{undertime}{inconclusive} {weekly_time_of_work} {time_under_over}\n")




#----------------------------------- END OF FUNCTIONS -------------------------------------



# stale odpowiadajace wartosciom w liscie zebranej z pliku "input.csv"
DATE  = 0   
EVENT = 1    
GATE  = 2 

# stale odpowiadajace indeksom w liscie skladajacej sie z [czasu_wejscia, czasu_wyjscia] (z biura)
ENTRY = 0
EXIT = 1


# utworzenie listy elementow z pominieciem naglowka
input_list = read_rows_from_input()  

# sprawdzenie poprawnosci wpisanych danych
validation_of_rows(input_list)  


# utworzenie slownika z kluczami odpowiadajacymi unikalnym dniom tygodnia
dict_of_days = make_dict_of_days(input_list)



fill_day_with_worktime(input_list)


# oblicza czas pracy konkretnego dnia
for day in dict_of_days.values():
    get_sum_of_time(day)


# wpisanie wynikow do pliku result
write_data_to_result(dict_of_days)

    
        
     