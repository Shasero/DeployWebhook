from aiogram import F, Router, Bot, html
from aiogram.types import Message, CallbackQuery, document
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv

import os

from openai import chat
import database.requests as rq
import keyboards.keyboard as kb

router = Router()

load_dotenv()

admin_id = os.getenv('ADMIN_ID')
intadmin_id = int(admin_id)
admin_id2 = os.getenv('ADMIN_ID2')
intadmin_id2 = int(admin_id2)


@router.callback_query(F.data.startswith('keyboardrassilka'))
async def rassilka(callback: CallbackQuery, bot: Bot):
    chat_id = callback.from_user.id
    last_message_id = callback.message.message_id
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await bot.delete_message(chat_id=chat_id, message_id=last_message_id)
    await callback.message.answer( 'Выберите что хотите отправить:', reply_markup=kb.list)


@router.callback_query(F.data == 'sendkurs')
async def kurs(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.answer('Все курсы в базе:', reply_markup=await kb.sendkeyboardkurs())


@router.callback_query(F.data.startswith('sendkurs_'))
async def kurssendall(callback: CallbackQuery, bot: Bot):
    await callback.answer('')
    selectkurs = callback.data.split('_')[1]
    kurssel = await rq.get_kurs(selectkurs)
    users = await rq.get_users()
    for kurs in kurssel:
        for user in users:
            try:
                await bot.send_message(chat_id=user.tg_id, text=f'{kurs.nameurl}\n{kurs.url}')
                if int(user.active != 1):
                    await rq.set_active(user.tg_id, 1)
            except:
                await rq.set_active(user.tg_id, 0)
                await callback.message.answer('Не успешная рассылка')

@router.callback_query(F.data == 'sendgaids')
async def gaids(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.answer('Все гайды в базе:', reply_markup=await kb.sendkeyboardgaid())


@router.callback_query(F.data.startswith('sendgaid_'))
async def gaidsendall(callback: CallbackQuery, bot: Bot):
    await callback.answer('')
    getgaid = callback.data.split('_')[1]
    gaidsel = await rq.get_gaid(getgaid)
    users = await rq.get_users()
    for gaid in gaidsel:
        for user in users:
            try:
                await bot.send_document(chat_id=user.tg_id, document=gaid.fail, caption=gaid.namefail)
                await callback.message.answer('Успешная рассылка')
                if int(user.active != 1):
                    await rq.set_active(user.tg_id, 1)
            except:
                await rq.set_active(user.tg_id, 0)
                await callback.message.answer('Не успешная рассылка')

    # await callback.message.answer('Успешная рассылка')