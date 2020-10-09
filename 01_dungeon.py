from decimal import Decimal
import re
import json
import csv
import datetime


class NotEnoughExpError(Exception):
    pass


class Game:
    def __init__(self, file):
        self.file = file
        self.dungeon = {}
        self.remaining_time = ''
        self.current_location_name = ''
        self.current_location = {}
        self.experience = 0
        self.time_elapsed = datetime.timedelta(seconds=0)

    def config(self):
        with open(self.file) as dungeon:
            self.dungeon = json.load(dungeon)
        self.remaining_time = '123456.0987654321'
        self.current_location_name = list(self.dungeon.keys())[0]
        self.current_location = self.dungeon[self.current_location_name]
        self.experience = 0
        self.time_elapsed = datetime.timedelta(seconds=0)

    def calculate_time(self, period):
        if '.' in period:
            dot = period.index('.')
            time_period = datetime.timedelta(seconds=int(period[:dot]), microseconds=int(period[dot + 1:dot + 7]))
            self.time_elapsed += time_period
        else:
            time_period = datetime.timedelta(seconds=int(period))
            self.time_elapsed += time_period
        remaining_time = Decimal(self.remaining_time) - Decimal(period)
        self.remaining_time = str(remaining_time)

    def fight_monster(self, monster):
        exp = re.search(r'exp\d+', monster).group()
        period = re.search(r'tm[\d\.]+', monster).group()
        self.experience += int(exp[3:])
        self.current_location.remove(monster)
        self.calculate_time(period[2:])

    def change_location(self, loc_dict):
        if list(loc_dict.keys())[0] == 'Hatch_tm159.098765432' and self.experience < 280:
            raise NotEnoughExpError('Вам не хватает сил открыть люк, нужно больше опыта')
        self.current_location_name = list(loc_dict.keys())[0]
        self.current_location = loc_dict[self.current_location_name]
        period = re.search(r'tm[\d\.]+', self.current_location_name).group()
        self.calculate_time(period[2:])

    def start(self):
        self.config()
        while True:
            if self.run():
                break
            else:
                self.config()

    def run(self):
        with open('log.csv', 'w', newline='') as log:
            writer = csv.writer(log)
            writer.writerow(['current_location', 'current_experience', 'current_date'])

        while True:
            if Decimal(self.remaining_time) < 0:
                print('Вы не успели добраться до люка. Загружаем автосейв. Да, он в самом начале.\n')
                return False
            if self.current_location_name == 'Hatch_tm159.098765432':
                print('Вы благополучно выбрались из подземелья')
                return True
            print('Вы находитесь в', self.current_location_name)
            print('У вас', str(self.experience), 'опыта и осталось', self.remaining_time, 'секунд до наводнения')
            print('Прошло времени:', self.time_elapsed)
            with open('log.csv', 'a', newline='') as log:
                writer = csv.writer(log)
                writer.writerow([self.current_location_name, self.experience, self.time_elapsed])
            print()
            print('Возможные действия:')
            counter = 1
            for item in self.current_location:
                if isinstance(item, str):
                    print(counter, 'Атаковать монстра', item)
                else:
                    print(counter, 'Перейти в локацию', list(item.keys())[0])
                counter += 1
            print(counter, 'Сдаться и выйти из игры')
            print()
            while True:
                choice = input('Ваш выбор: ')
                if not choice.isdigit() or not len(self.current_location) + 1 > int(choice) > 0:
                    print('Неверный выбор, попробуйте еще раз')
                else:
                    break
            choice = int(choice)
            if choice == len(self.current_location) + 1:
                return True
            elif isinstance(self.current_location[choice - 1], str):
                print('Вы выбрали сражаться с монстром', self.current_location[choice - 1], '\n')
                self.fight_monster(self.current_location[choice - 1])
            else:
                try:
                    self.change_location(self.current_location[choice - 1])
                    print('Вы переходите в локацию', self.current_location_name, '\n')
                except NotEnoughExpError as err:
                    print(err, '\n')


if __name__ == '__main__':
    game = Game('rpg.json')
    game.start()
