import base64, pickle
from django_redis import get_redis_connection


def merge_carts_cookie_redis(request, user, response):

    carts_str = request.COOKIES.get('carts')

    if not carts_str:
        return response

    cookie_cart_str_byte = carts_str.encode()

    cookie_cart_dict_byte = base64.b64decode(cookie_cart_str_byte)

    cookie_cart_dict = pickle.loads(cookie_cart_dict_byte)

    new_cart_dict = {}
    new_selected_add = []
    new_selected_rem = []

    for sku_id, cookie_dict in cookie_cart_dict.items():
        # new_cart_dict[sku_id] = {
        #     'count':cookie_dict['count']
        # }

        new_cart_dict[sku_id] = cookie_dict['count']
        if cookie_dict['selected']:
            new_selected_add.append(sku_id)
        else:
            new_selected_rem.append(sku_id)

    redis_conn = get_redis_connection('carts')
    pl = redis_conn.pipeline()

    pl.hmset('carts_%s' % user.id, new_cart_dict)
    if new_selected_add:
        pl.sadd('selected_%s' % user.id, *new_selected_add)
    if new_selected_rem:
        pl.srem('selected_%s' % user.id, *new_selected_rem)
    pl.execute()

    response.delete_cookie('carts')

    return response
