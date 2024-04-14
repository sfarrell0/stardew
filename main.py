import csv
import random
import numpy as np
def run_fishing_table(fishing_xp, location="Mountain", force_perfect=False, verbose=False):
    #Data taken from https://stardewvalleywiki.com/Fishing


    #Calculate current fishing level
    xp_thresholds = [100, 380, 770, 1300, 2150, 3300, 4800, 6900, 10000, 15000]
    fishing_level = 0
    for i in xp_thresholds:
        if fishing_xp > i:
            fishing_level += 1
        else:
            break

    quality_probs = [ #(cumulative)
        [.42, .99, 1], #Fishing Zone 3 at level 0
        [.2, .59, 1], #Fishing Zone 5 for level 1+ since they get +1 cast distance
        [0, .49, 1],
        [0, .49, 1],
        [0, .32, 1],
        [0, .32, 1],
        [0, 0, 1],
        [0, 0, 1],
        [0, 0, 1],
        [0, 0, 1],
        [0, 0, 1]
    ]
    fish_table = { #Name, difficulty, chance,
        "Mountain":[
            ["Largemouth Bass", 50,.1881, 100],
            ["Carp", 15, .2166, 30],
            ["Green Algae", 5, .1351, 15],
            ["Bullhead", 46, .1610, 75],
            ["Chub", 35, .2166, 50]
        ]
    }

    time_cost_min = 0.6
    time_cost_max = 30 - fishing_level * 0.25
    time_cost = time_cost_min + (time_cost_max - time_cost_min) * random.random()
    time_cost = max(0.5, time_cost * 0.75)  # assume the player doesn't miss a hook since it is trivial


    chosen_table = fish_table[location]
    roll = random.random()
    cumul = 0
    trash = True
    for fish in chosen_table:
        cumul += fish[2]
        if cumul > roll:
            trash = False
            break
    if trash:
        return 0, 3, time_cost
    else:
        fish_value = fish[3]



    quality_table = quality_probs[fishing_level]
    roll = random.random()
    quality = 0
    for i in range(3):
        if roll < quality_table[i]:
            quality = i
            break
    difficulty = fish[1]
    xp = (quality + 1) * 3 + (difficulty / 3)


    perfect_catch = force_perfect#random.random() < 0.2 or force_perfect
    if perfect_catch:
        xp *= 2.4
    if perfect_catch: #Upgrade quality on perfect catch unless
        quality += (1 if quality != 0 else 0)

    quality_mods = [1,1.25,1.5,2]
    fish_value *= quality_mods[quality]
    fish_value = int(fish_value)




    if verbose:
        print(f"Caught {fish[0]} at quality {quality} and sold for {fish_value} at fishing level {fishing_level}")
    return fish_value, int(xp), time_cost
def run_simulation(protocol, verbose=False, perfect_fishing=False):

    gold = 500
    total_profit = 500 + 20*15
    day = 1
    fishing_xp = 0

    #crop, days left, count
    field = [
        ["parsnip", 5, 15, False]
    ]
    #crop: (price, days to grow)
    base_shop = {
        "parsnip": (20, 4),
        "garlic": (40, 4),
        "potato": (50, 6),
        "kale": (70, 6),
        "cauliflower": (80, 12),
        "green bean": (60, 10),
        "strawberries": (100, 8)
    }
    regrow_days = {
        "green bean": 3,
        "strawberries": 4
    }
    single_sale_price = {
        "parsnip": 35,
        "cauliflower": 175,
        "kale": 110,
        "garlic": 60,
        "green bean": 40,
        "strawberries": 120,
        "potato": 80
    }
    crop_reroll_chances = {
        "parsnip": 0,
        "cauliflower": 0,
        "kale": 0,
        "garlic": 0,
        "green bean": 0,
        "strawberries": 0.02,
        "potato": 0.2
    }
    tilled_tiles = 15
    tiles_in_use = 15
    profits = []
    energies = []
    while day <= 28:
        if verbose:
            print(f"======[ Day {day} ]=====")
        day_time = 0
        player_energy = 270
        if day == 1:
            player_energy -= 15*2 #(tilled
        #====Grow crops=====
        new_field = []
        for crop in field:
            if crop[1] == 1:
                day_time += 0.33 * crop[2]
                if crop[0] in regrow_days:
                    #reset plant!
                    new_field.append([crop[0], regrow_days[crop[0]], crop[2], True])
                else:
                    tiles_in_use -= crop[2]

                for i in range(crop[2]):
                    gold += single_sale_price[crop[0]]
                    total_profit += single_sale_price[crop[0]] - shop[crop[0]][0]
                    if crop[3] == True:
                        total_profit += shop[crop[0]][0]
                    while random.random() < crop_reroll_chances[crop[0]]:
                        gold += single_sale_price[crop[0]]
                        total_profit += single_sale_price[crop[0]]

            else:
                day_time += 0.33 * crop[2]
                if crop[2]*2 <= player_energy:
                    new_field.append([crop[0], crop[1]-1, crop[2], crop[3]])
                    player_energy -= crop[2]*2
                else:
                    new_field.append([crop[0], crop[1] - 1, player_energy //2, crop[3]])
                    player_energy -= player_energy //2 * 2
                    new_field.append([crop[0], crop[1], crop[2]-player_energy //2, crop[3]])

        field = new_field
        #====Purchase crops====
        #add strawberries to the shop for Spring 13 only
        #print(f"Money entering shop: {gold}")
        shop = base_shop
        days_left = 28 - day #(we don't want to buy crops if they won't grow in time)
        days_to_strawberry = 13 - day
        for crop in protocol:
            if "strawberries" in protocol:
                if day == 13:
                    if crop == "strawberries":
                        purchase_count = min(gold // shop[crop][0], player_energy //4)
                        if purchase_count > 0:
                            gold -= purchase_count * shop[crop][0]
                            field.append([crop, shop[crop][1], purchase_count, False])
                            player_energy -= purchase_count * 4
                            day_time += 1 * purchase_count
                    else:
                        continue
                else:
                    if crop == "strawberries":
                        continue
                    grow_time = shop[crop][1]
                    if grow_time <= days_left and (day > 13 or grow_time <= days_to_strawberry):
                        purchase_count = min(gold // shop[crop][0], player_energy //4)
                        if purchase_count > 0:
                            gold -= purchase_count * shop[crop][0]
                            field.append([crop, shop[crop][1], purchase_count, False])
                            player_energy -= purchase_count * 4
                            day_time += 1 * purchase_count
            else:
                grow_time = shop[crop][1]
                if grow_time <= days_left:
                    purchase_count = min(gold // shop[crop][0], player_energy //4)
                    if purchase_count > 0:
                        gold -= purchase_count * shop[crop][0]
                        field.append([crop, shop[crop][1], purchase_count, False])
                        player_energy -= purchase_count * 4
                        day_time += 1 * purchase_count

        if day > 1:
            while player_energy >= 8 and day_time < 860:
                player_energy -= 8
                fished, xp, time_cost = run_fishing_table(fishing_xp, verbose=verbose, force_perfect=perfect_fishing)
                day_time += time_cost
                fishing_xp += xp
                total_profit += fished
                gold += fished
        #print(f"Day {day}, total_profit={total_profit}, energy ={player_energy} field={field}")
        day += 1
        profits.append(total_profit)
        energies.append(player_energy)
    return energies, profits, gold



if __name__ == '__main__':

    filename = "stardewSpringTest.csv"
    protocol_list = [
        ["Parsnips", ["parsnip"], False],
        ["Cauliflowers", ["cauliflower"], False],
        ["Potatoes", ["potato"], False],
        ["Kale", ["kale"], False],
        ["Garlic", ["garlic"], False],
        ["Strawberry Potato", ["strawberries", "potato"], False],
        ["Strawberry Parsnip", ["strawberries", "parsnip"], False],
        ["Fishing", [], False],
        ["Perfect Fishing", [], True]
    ]
    # protocol_list = [
    #     ["Fishing", []]
    # ]
    fields = ["Day"]
    rows = []
    for i in range(1, 29):
        fields.append(i)

    n = 100
    for protocol in protocol_list:
        row = [protocol[0]]

        profit_avg = np.zeros((28))
        energy_avg = np.zeros((28))
        gold_avg = 0
        for i in range(n):
            energies, profits, gold = run_simulation(protocol[1], verbose=False, perfect_fishing=protocol[2])
            profit_avg += np.array(profits)
            energy_avg += np.array(energies)
            gold_avg += gold
        energy_avg /= n
        profit_avg /= n
        gold_avg /= n
        row.extend(profit_avg.tolist())
        rows.append(row)
        #print(" ".join([str(i) for i in profit_avg.tolist()]))
        #print(profit_avg.tolist())

    with open(filename, 'w', newline="") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(fields)
        csvwriter.writerows(rows)



