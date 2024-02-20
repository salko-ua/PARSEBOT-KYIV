import re
import requests
from aiogram import types
from bs4 import BeautifulSoup
from aiogram.fsm.context import FSMContext
from typing import Optional
from src.handlers import keyboards
from src.handlers import telegram

def get_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    return soup

class Information():
    def get_photo(soup: BeautifulSoup, a_lot_of: bool) -> [list, types.URLInputFile]:
        photo = soup.find("div", class_="swiper-wrapper").find_all("img")

        list_src_photo = []
        media_group = [] 

        for src in photo:
            list_src_photo.append(src.get("src"))

        if len(list_src_photo) > 10:
            del list_src_photo[10:]
       
        for photo_url in list_src_photo:
            media_group.append(types.InputMediaPhoto(media=photo_url))

        first_photo = types.URLInputFile(str(list_src_photo[0]))
        
        if not a_lot_of:
            return first_photo
        
        return media_group
        
    def get_tag(soup: BeautifulSoup) -> [int, int, str]:
        # constants to check the list "tags"
        NEED_WORDS_RUSSIAN = ["Количество комнат:", "Общая площадь:",
                              "Этаж:", "Этажность:"]
        NEED_WORDS_UKRAINIAN = ["Кількість кімнат:",
                                "Загальна площа:","Поверх:", "Поверховість:"]
        # parsing tags from the page
        tags = soup.find("ul", class_="css-sfcl1s").find_all("p")
        all_tag_text = []

        for need_word in NEED_WORDS_RUSSIAN:
            for tag in tags:
                if need_word in tag.text:
                    all_tag_text.append(tag.text)
        
        for need_word in NEED_WORDS_UKRAINIAN:
            for tag in tags:
                if need_word in tag.text:
                    all_tag_text.append(tag.text)
        
        count_room = int((re.search(r"\d+", all_tag_text[0])).group())
        count_area = int((re.search(r"\d+", all_tag_text[1])).group())
        flour_have = int((re.search(r"\d+", all_tag_text[2])).group())
        flour_everything = int((re.search(r"\d+", all_tag_text[3])).group())
        flour = f"{flour_have}/{flour_everything}"

        return count_room, count_area, flour
            
    def get_money(soup: BeautifulSoup) -> [str, str]:
        # parsing money from the page
        money = soup.find("h2", text=re.compile(r'.*грн.*'))
    
        if not money:
            money = soup.find("h3", text=re.compile(r'.*грн.*'))

        if not money:
            money = soup.find("h4", text=re.compile(r'.*грн.*'))

        if not money:
            return "Суму не знайдено", "#0грн"
        
        without_space = "".join(money.text.split())
        price = int((re.search(r"\d+", without_space)).group())

        return money.text, get_tags_for_money(price) 

    def get_caption(soup: BeautifulSoup) -> str:
        # parsing caption from the page
        caption = soup.find("div", class_="css-1t507yq er34gjf0")

        if not caption:
            return "Описание не найдено"

        if len(caption.text) > 800:
           return caption.text[0:800]

        return caption.text
    
    def get_header(soup: BeautifulSoup) -> [str, str]:
        # parsing caption from the page
        header = soup.find("h4", class_="css-1juynto")

        if not header:
            return None

        return header.text
    
    def get_city_and_district(soup: BeautifulSoup) -> str:
        find = soup.find_all("script")
        
        pattern_district = re.compile(r'\\"districtName\\":\\"([^\\"]+)\\"')
        pattern_city = re.compile(r'\\"cityName\\":\\"([^\\"]+)\\"')

        for one in find:
            district = pattern_district.search(one.text)
            if district:
                break
        
        for one in find:
            city = pattern_city.search(one.text)
            if city:
                break


        # first variant - TWO GROUP
        if city and district:
            return city.group(1), district.group(1)
        
        # middle variant - ONE GROUP, ONE STR
        if city and not district:
            return city.group(1), ""
        elif not city and district:
            return "", district.group(1)

        # last variant - TWO STR
        if not city:
            city = ""

        if not district:
            district = ""

        return city, district

    def get_owner(soup: BeautifulSoup) -> str:
        return (soup.find("h4", class_="css-1lcz6o7 er34gjf0").text)

    def create_pieces_caption(soup: BeautifulSoup) -> str:
        caption = Information.get_caption(soup)
        header = Information.get_header(soup)
        city, district = Information.get_city_and_district(soup)
        owner = Information.get_owner(soup)

        count_room, count_area, flour = Information.get_tag(soup)
        money, teg_money = Information.get_money(soup)

        if not district:
            tag_district = city
        elif district:
            tag_district = district

        main_caption = (f"🏡{count_room}к кв\n"
            f"🏢Поверх: {flour}\n"
            f"🔑Площа: {count_area}м2\n"
            f'📍Район: {tag_district}\n'
            f"💳️{money}"
            f"\n\n{header}\n\n"
            f"📝Опис: {caption}"
            f"\n\n#{count_room}ККВ #{teg_money} #{tag_district}\n\n"
            f"📞Зв`язок тут:\n"
            f"👤Власник: {owner}\n")

        return main_caption
    
    def get_edit_caption(caption, phone_number: Optional[str] = None):
        if phone_number == None:
            phone_number = ""
        return (f"{caption}📱Номер: {phone_number}")
    
# Отримання тегу залежно від ціни
def get_tags_for_money(price): #good
    if 5000 <= price <= 7000:
        return "50007000грн"
    elif 7000 <= price <= 9000:
        return "70009000грн"
    elif 9000 <= price <= 11999:
        return "900012000грн"
    elif 12000 <= price <= 14000:
        return "1200014000грн"
    elif 14000 <= price <= 15000:
        return "1400015000грн"
    elif 15000 <= price <= 18000:
        return "1500018000грн"
    elif 18000 <= price <= 20000:
        return "1800020000грн"
    elif 20000 <= price <= 25000:
        return "2000025000грн"
    elif 25000 <= price <= 30000:
        return "2500030000грн"
    elif 30000 <= price <= 35000:
        return "3000035000грн"
    elif 35000 <= price <= 40000:
        return "3500040000грн"
    elif price >= 40000:
        return "Выше40000грн"
    

# Отримання всіх даних і запуск надсилання
async def get_data(message: types.Message, state: FSMContext):
    soup: BeautifulSoup = get_url(message.text)
    first_photo = Information.get_photo(soup, False)
    caption = Information.create_pieces_caption(soup)

    await state.set_state(telegram.Edit.control)
    await state.update_data(soup=soup)
    await message.answer_photo(caption=caption, photo=first_photo, reply_markup=keyboards.edit_kb())


