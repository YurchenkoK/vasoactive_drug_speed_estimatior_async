// src/mock/DrugMock.ts
import type { Drug } from "../DrugTypes";

export const mockDrugs: Drug[] = [
    {
        id: 1,
        name: "Адреналин",
        description: "Применяется при анафилактическом шоке, остановке сердца, тяжелой бронхиальной астме",
        image_url: "http://localhost:9000/images/adrenaline.jpg",
        concentration: 1.0,
        volume: 1.0,
        is_active: true,
    },
    {
        id: 2,
        name: "Норадреналин",
        description: "Используется при острой артериальной гипотензии, шоковых состояниях различной этиологии",
        image_url: "http://localhost:9000/images/noradrenaline.jpg",
        concentration: 2.0,
        volume: 4.0,
        is_active: true,
    },
    {
        id: 3,
        name: "Добутамин",
        description: "Показан при острой сердечной недостаточности, кардиогенном шоке",
        image_url: "http://localhost:9000/images/dobutamine.jpg",
        concentration: 12.5,
        volume: 20.0,
        is_active: true,
    },
    {
        id: 4,
        name: "Дофамин",
        description: "Применяется при шоковых состояниях, сердечной недостаточности, почечной недостаточности",
        concentration: 40.0,
        volume: 5.0,
        is_active: true,
    },
    {
        id: 5,
        name: "Эпинефрин",
        description: "Используется для лечения анафилаксии, остановки сердца, тяжелых аллергических реакций",
        concentration: 1.0,
        volume: 1.0,
        is_active: true,
    },
];
