from aiogram import F, Router, types
from aiogram.filters import Command
from main import bot
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from handlers.parser import get_data, Information
from handlers.keyboards import repost_kb

router = Router()

class Edit(StatesGroup):
    phone_number = State()
    control = State()

# ===========================start============================
@router.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        f"Вітаю {message.from_user.full_name}! 👏\n"
        "Цей бот призначений для швидкого парсингу і створення постів у telegram з OLX.ua\n"
        "Приємного користування 😁",
        disable_web_page_preview=True)

@router.message(F.text.startswith("https://www.olx.ua/"))
async def main(message: types.Message, state: FSMContext):
    try:
        await get_data(message, state)
    except Exception:
        await message.answer(
            f"Виникла помилка ❌\nСторінку не вдалося обробити\n",
            reply_markup=types.ReplyKeyboardRemove(),
        )


@router.callback_query(F.data == "Репост в канал ▶️", Edit.control)
async def repost_to_channel(query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    soup = data["soup"]
    phone_number = data["phone_number"]
    media_group = Information.get_photo(soup, True)
    caption = Information.create_pieces_caption(soup)
    full_caption = Information.get_edit_caption(caption, phone_number)

    await state.clear()
    await query.message.edit_reply_markup(reply_markup=None)

    media_messages = await bot.send_media_group(-1001610806063, media=media_group)
    await bot.edit_message_caption(chat_id=-1001610806063, 
                                   message_id=media_messages[0].message_id,
                                   caption=full_caption)

@router.callback_query(F.data == "Додати номер ✏️", Edit.control)
async def edit_number(query: types.CallbackQuery, state: FSMContext):
   await query.answer("Надішліть номер", show_alert=True)
   await state.set_state(Edit.phone_number)
   await query.message.delete()

@router.message(Edit.phone_number)
async def edit_number(message: types.Message, state: FSMContext):
    await state.update_data(phone_number=message.text)
    data = await state.get_data()
    soup = data["soup"]
    first_photo = Information.get_photo(soup, False)
    caption = Information.create_pieces_caption(soup)
    all_caption = Information.get_edit_caption(caption, phone_number=message.text)
    await message.answer_photo(caption=all_caption, photo=first_photo, reply_markup=repost_kb())
    await state.set_state(Edit.control)

@router.message()
async def all_message(message: types.Message):
    await message.answer(
        "🔴 Вибачте, але мені потрібне тільки посилання на сторінку olx.ua з нерухомістю.\n"
        "У форматі https://www.olx.ua/...",
        disable_web_page_preview=True,
    )