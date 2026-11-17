import pytest
from django.db import connection
from django.test import Client
from django.urls import reverse

from reviews.forms import ReviewForm
from reviews.models import Review

pytestmark = pytest.mark.django_db


def test_root_redirects_to_reviews(client):
    response = client.get(reverse("reviews:index"))
    assert response.status_code == 302
    assert response.url == reverse("reviews:review_list")


def test_list_renders_saved_reviews(client):
    Review.objects.create(author="Алексей", text="Первый отзыв")
    Review.objects.create(author="Мария", text="Второй отзыв")

    response = client.get(reverse("reviews:review_list"))
    assert response.status_code == 200

    reviews_in_context = list(response.context["reviews"])
    assert len(reviews_in_context) == 2
    # Сортировка: новые сверху
    assert [r.author for r in reviews_in_context] == ["Мария", "Алексей"]

    html = response.content.decode()
    assert "Алексей" in html
    assert "Первый отзыв" in html
    assert "Мария" in html
    assert "Второй отзыв" in html


def test_form_creates_review_and_redirects(client):
    payload = {
        "author": "   Иван Иванов   ",
        "text": "   Замечательный проект!   ",
    }
    response = client.post(reverse("reviews:review_list"), payload)
    # Post/Redirect/Get: после успешного POST перенаправляем на список
    assert response.status_code == 302
    assert response.url == reverse("reviews:review_list")

    # Проверяем, что отзыв сохранён с удалением лишних концевых пробелов
    review = Review.objects.get()
    assert review.author == "Иван Иванов"
    assert review.text == "Замечательный проект!"
    assert Review.objects.count() == 1

    # Повторный GET не дублирует данные (F5 безопасен)
    follow_response = client.get(response.url)
    assert follow_response.status_code == 200
    assert Review.objects.count() == 1


@pytest.mark.parametrize(
    "payload, expected_field_error",
    [
        ({"author": "", "text": "Хороший сайт"}, "author"),
        ({"author": "   ", "text": "Хороший сайт"}, "author"),
        ({"author": "x" * 121, "text": "Хороший сайт"}, "author"),
        ({"author": "Иван", "text": ""}, "text"),
        ({"author": "Иван", "text": "   "}, "text"),
        ({"author": "", "text": ""}, "author"),
        ({"author": "   ", "text": "   "}, "author"),
    ],
)
def test_invalid_input_is_rejected(client, payload, expected_field_error):
    response = client.post(reverse("reviews:review_list"), payload)
    assert response.status_code == 400
    assert expected_field_error in response.context["form"].errors
    assert not Review.objects.exists()


def test_model_form_accepts_author_at_maximum_length():
    form = ReviewForm({"author": "x" * 120, "text": "Тестовый отзыв"})
    assert form.is_valid()
    review = form.save()
    assert len(review.author) == 120


def test_template_escapes_user_input(client):
    dangerous_author = "<script>alert('author')</script>"
    dangerous_text = "<script>alert('text')</script>"
    Review.objects.create(author=dangerous_author, text=dangerous_text)

    html = client.get(reverse("reviews:review_list")).content.decode()
    assert "<script>" not in html
    assert "&lt;script&gt;alert(&#x27;author&#x27;)&lt;/script&gt;" in html or "&lt;script&gt;" in html


def test_post_requires_csrf_token():
    enforcing_client = Client(enforce_csrf_checks=True)
    url = reverse("reviews:review_list")

    # Запрос без CSRF-токена должен отклоняться с кодом 403
    response_no_csrf = enforcing_client.post(url, {"author": "Хакер", "text": "Без CSRF"})
    assert response_no_csrf.status_code == 403
    assert not Review.objects.exists()

    # С CSRF-токеном запрос успешен
    get_res = enforcing_client.get(url)
    assert get_res.status_code == 200
    csrf_token = enforcing_client.cookies["csrftoken"].value

    response_with_csrf = enforcing_client.post(
        url,
        {
            "author": "Честный пользователь",
            "text": "С правильным токеном",
            "csrfmiddlewaretoken": csrf_token,
        },
    )
    assert response_with_csrf.status_code == 302
    assert Review.objects.filter(author="Честный пользователь").exists()


def test_admin_requires_login(client):
    response = client.get(reverse("admin:reviews_review_changelist"))
    assert response.status_code == 302
    assert response.url.startswith(reverse("admin:login"))


def test_admin_displays_and_searches_reviews(admin_client):
    Review.objects.create(author="Сергей Смирнов", text="Отзыв от Сергея")
    Review.objects.create(author="Ольга Иванова", text="Отзыв от Ольги")

    url = reverse("admin:reviews_review_changelist")

    # Проверка отображения списка в админке
    response = admin_client.get(url)
    assert response.status_code == 200
    assert "Сергей Смирнов" in response.content.decode()
    assert "Ольга Иванова" in response.content.decode()

    # Проверка поиска по автору
    search_response = admin_client.get(url, {"q": "Сергей"})
    assert search_response.status_code == 200
    content = search_response.content.decode()
    assert "Сергей Смирнов" in content
    assert "Ольга Иванова" not in content


def test_data_persistence_after_db_reconnect():
    Review.objects.create(author="Постоянный автор", text="Данные должны сохраниться")
    connection.close()

    # После закрытия и повторного обращения запись должна присутствовать
    reloaded = Review.objects.get(author="Постоянный автор")
    assert reloaded.text == "Данные должны сохраниться"
