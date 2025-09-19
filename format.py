def num_format(num=int):
    if num < 1000:
        return num
    else:
        strnum = str(num)
        three_digit = len(strnum)//3
        extra_digit = len(strnum)%3
        splited_number = []
        formatted_txt = ""
        for i in strnum:
            splited_number.append(i)
        if extra_digit > 0:
            splited_number.insert(extra_digit, ",")
        elif extra_digit == 0:
            extra_digit = 3
            three_digit -= 1
            splited_number.insert(extra_digit, ",")
        while three_digit > 1:
            extra_digit += 4
            splited_number.insert(extra_digit, ",")
            three_digit -= 1
        for j in splited_number:
            formatted_txt = formatted_txt + j
        return formatted_txt


def num_unformat(formatted_int=str):
    splitted_formatted_number = []
    formatted_txt = ""
    for i in formatted_int:
        splitted_formatted_number.append(i)
    for j in splitted_formatted_number:
        if j == ",":
            splitted_formatted_number.remove(",")
    for k in splitted_formatted_number:
        formatted_txt = formatted_txt + k
    return int(formatted_txt)
    
    


    