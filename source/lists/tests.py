from django.core.urlresolvers import resolve
from django.template.loader import render_to_string
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.http import HttpRequest

from lists.views import home_page
from lists.models import Item, List

class HomePageTest(StaticLiveServerTestCase):

    def test_use_home_template(self):
        response = self.client.get("/")
        self.assertTemplateUsed(response, "home.html")


class ListAndItemModelTest(StaticLiveServerTestCase):

    def test_saving_and_retrieving_items(self):
        list_ = List()
        list_.save()

        first_item = Item()
        first_item.text = "The 1st item"
        first_item.list = list_
        first_item.save()

        second_item = Item()
        second_item.text = "2nd item"
        second_item.list = list_
        second_item.save()

        saved_list = List.objects.first()
        self.assertEqual(saved_list, list_)

        saved_items = Item.objects.all()
        self.assertEqual(saved_items.count(), 2)

        first_saved_item = saved_items[0]
        second_saved_item = saved_items[1]
        self.assertEqual(first_saved_item.text, "The 1st item")
        self.assertEqual(first_saved_item.list, list_)
        self.assertEqual(second_saved_item.text, "2nd item")
        self.assertEqual(second_saved_item.list, list_)


class ListViewTest(StaticLiveServerTestCase):

    def test_uses_list_template(self):
        list_ = List.objects.create()
        response = self.client.get("/lists/{}/".format(list_.id))
        self.assertTemplateUsed(response, "list.html")

    def test_display_all_items(self):
        correct_list = List.objects.create()
        Item.objects.create(text="item 1", list=correct_list)
        Item.objects.create(text="item 2", list=correct_list)
        other_list = List.objects.create()
        Item.objects.create(text="other item 1", list=other_list)
        Item.objects.create(text="other item 2", list=other_list)

        response = self.client.get("/lists/{}/".format(correct_list.id))

        self.assertContains(response, "item 1")
        self.assertContains(response, "item 2")
        self.assertNotContains(response, "other item 1")
        self.assertNotContains(response, "other item 2")

    def test_passes_correct_list_to_view(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()
        response = self.client.get("/lists/{}/".format(correct_list.id))
        self.assertEqual(response.context["list"], correct_list)


class NewListTest(StaticLiveServerTestCase):

    def test_can_save_POST_request(self):
        response = self.client.post("/lists/new", data={"item_text": "A new list item"})

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, "A new list item")

    def test_redirect_after_POST(self):
        response = self.client.post("/lists/new", data={"item_text": "A new list item"})
        new_list = List.objects.first()
        self.assertRedirects(response, "/lists/{}/".format(new_list.id))


class NewItemTest(StaticLiveServerTestCase):

    def test_can_save_a_POST_request_to_an_existing_list(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()

        self.client.post(
                "/lists/{}/add_item".format(correct_list.id),
                data={"item_text": "A new item for existing list"}
                )

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, "A new item for existing list")
        self.assertEqual(new_item.list, correct_list)

    def test_redirects_to_list_view(self):
        other_list = List.objects.create()
        correct_list = List.objects.create()

        response = self.client.post(
                "/lists/{}/add_item".format(correct_list.id),
                data={"item_text": "A new item for existing list"}
                )

        self.assertRedirects(response, "/lists/{}/".format(correct_list.id))
