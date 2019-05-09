import string
import random


def id_generator(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def str_year_month(datetime):
    return f'{datetime.year}-{datetime.month}'


def init_dict_key_month_between(from_date, to_date):
    month_dict = {}
    temp_year, temp_month = from_date.year, from_date.month

    while temp_year*100+temp_month <= to_date.year*100+to_date.month:
        month_dict[f'{temp_year}-{temp_month}'] = 0
        if temp_month == 12:
            temp_year += 1
            temp_month = 1
        else:
            temp_month += 1
    return month_dict


def top_customer_data_from_tickets(tickets, num=5):
    commision = {}
    num_of_tickets = {}

    for ticket in tickets:
        if ticket.customer_email not in commision:
            commision[ticket.customer_email] = ticket.commision
            num_of_tickets[ticket.customer_email] = 1
        else:
            commision[ticket.customer_email] += ticket.commision
            num_of_tickets[ticket.customer_email] += 1

    top_customers = (sorted(commision,
                            key=commision.__getitem__, reverse=True))[:num]

    top_commision = []
    top_num_of_tickets = []
    for customer in top_customers:
        top_commision.append(float(commision[customer]))
        top_num_of_tickets.append(num_of_tickets[customer])

    return top_customers, top_commision, top_num_of_tickets


def top_booking_agent_data_from_tickets(tickets, num=5):
    commision = {}
    num_of_tickets = {}

    for ticket in tickets:
        if ticket.seller.email not in commision:
            commision[ticket.seller.email] = ticket.commision
            num_of_tickets[ticket.seller.email] = 1
        else:
            commision[ticket.seller.email] += ticket.commision
            num_of_tickets[ticket.seller.email] += 1
    top_booking_agents = (sorted(commision,
                                 key=commision.__getitem__, reverse=True))[:num]

    top_commision = []
    top_num_of_tickets = []
    for customer in top_booking_agents:
        top_commision.append(float(commision[customer]))
        top_num_of_tickets.append(num_of_tickets[customer])

    return top_booking_agents, top_commision, top_num_of_tickets


def frequent_customer_data_from_tickets(tickets, num=5):
    num_of_tickets = {}

    for ticket in tickets:
        if ticket.customer_email not in num_of_tickets:
            num_of_tickets[ticket.customer_email] = 1
        else:
            num_of_tickets[ticket.customer_email] += 1

    top_customers = (sorted(num_of_tickets,
                            key=num_of_tickets.__getitem__, reverse=True))[:num]

    top_num_of_tickets = []
    for customer in top_customers:
        top_num_of_tickets.append(num_of_tickets[customer])

    return top_customers, top_num_of_tickets
