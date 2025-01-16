from payroll.googledocshandler import GoogleDocsApiHandler


def write_google_doc(trucker, pay_date_week_ending, to_be_paid):
    handler = GoogleDocsApiHandler()
    document_name = f'{trucker.name} - PAY Week Ending {pay_date_week_ending}'
    document_id = handler.create(document_name)


    """
    Mazarura Transport & Logistics LLC 

    Antonio Brown PAY STATEMENT  - Week Ending November 30th, 2024
    Truck 1010
    ----------------------------------------------------------------------------------------------------------------------------
    	DATE 	   	Company  			RC/ LOAD			AMOUNT 
    ---------------------------------------------------------------------------------------------------------------------------- 

    """

    # so index is calculated by the number of characters in strings
    driver_name = trucker.name
    pay_date_week_ending = pay_date_week_ending
    truck_name = trucker.truck

    company_name_header = "Mazarura Transport & Logistics LLC \n"
    secondary_name_driver = f"{driver_name} PAY STATEMENT - Week Ending {pay_date_week_ending} \n"
    truck = f"Truck {truck_name}"
    current_index = 1
    end_index = len(company_name_header)

    request_header = [
        {
            'insertText': {
                'location': {
                    'index': current_index,  # Position to insert text
                },
                'text': f'{company_name_header}'
            }
        },
        {
            'updateTextStyle': {
                'range': {
                    'startIndex': current_index,  # Start index of the text
                    'endIndex': end_index,  # End index of the text
                },
                'textStyle': {
                    'bold': True,
                    'underline': True,
                    'fontSize': {
                        'magnitude': 14,  # Font size
                        'unit': 'PT'  # Points
                    }
                },
                'fields': 'bold,underline,fontSize'
            }
        }
    ]

    current_index = end_index
    end_index = end_index + len(secondary_name_driver) + len(truck)

    req_driver_pay_ending_and_truck_name = [
        {
            'insertText': {
                'location': {
                    'index': current_index,  # Position to insert text
                },
                'text': f'\n{secondary_name_driver}{truck}'
            }
        },
        {
            'updateTextStyle': {
                'range': {
                    'startIndex': current_index,  # Start index of the text
                    'endIndex': end_index,  # End index of the text
                },
                'textStyle': {
                    'bold': True,
                    'underline': False,
                    'fontSize': {
                        'magnitude': 11,  # Font size
                        'unit': 'PT'  # Points
                    }
                },
                'fields': 'bold,underline,fontSize'
            }
        },

    ]

    loads_header_text = """
----------------------------------------------------------------------------------------------------------------------------
DATE 	   	Company  			RC/ LOAD				AMOUNT 
---------------------------------------------------------------------------------------------------------------------------- 
"""

    current_index = end_index
    end_index = end_index + len(loads_header_text)
    req_loads_header = [
        {
            'insertText': {
                'location': {
                    'index': current_index,  # Position to insert text
                },
                'text': f'\n{loads_header_text}'
            }
        },
        {
            'updateTextStyle': {
                'range': {
                    'startIndex': current_index,  # Start index of the text
                    'endIndex': end_index,  # End index of the text
                },
                'textStyle': {
                    'bold': True,
                    'underline': False,
                    'fontSize': {
                        'magnitude': 10,  # Font size
                        'unit': 'PT'  # Points
                    }
                },
                'fields': 'bold,underline,fontSize'
            }
        },
    ]

    handler = GoogleDocsApiHandler()
    handler.batch_put(document_id, request_header)
    handler.batch_put(document_id, req_driver_pay_ending_and_truck_name)
    handler.batch_put(document_id, req_loads_header)
    line = '\n'
    for trip in trucker.trips:
        line += f'{trip.date:<8} 	{trip.broker:<25}  		{trip.rate_con:<10}			{trip.rate:<7}\n'

    current_index = end_index
    end_index = end_index + len(line)

    loads_req = [
        {
            'insertText': {
                'location': {
                    'index': current_index,  # Position to insert text
                },
                'text': line
            }
        },
        {
            'updateTextStyle': {
                'range': {
                    'startIndex': current_index,  # Start index of the text
                    'endIndex': end_index,  # End index of the text
                },
                'textStyle': {
                    'bold': False,
                    'underline': False,
                    'fontSize': {
                        'magnitude': 10,  # Font size
                        'unit': 'PT'  # Points
                    }
                },
                'fields': 'bold,underline,fontSize'
            }
        },
    ]

    handler.batch_put(document_id, loads_req)

    total_revenue_lines = f"""
----------------------------------------------------------------------------------------------------------------------------
Total for 100% Line Haul Revenue ${trucker.total_money}
----------------------------------------------------------------------------------------------------------------------------
"""

    current_index = end_index - 1
    end_index = end_index + len(total_revenue_lines)

    total_loads_req = [
        {
            'insertText': {
                'location': {
                    'index': current_index,  # Position to insert text
                },
                'text': total_revenue_lines
            }
        },
        {
            'updateTextStyle': {
                'range': {
                    'startIndex': current_index,  # Start index of the text
                    'endIndex': end_index,  # End index of the text
                },
                'textStyle': {
                    'bold': True,
                    'underline': False,
                    'fontSize': {
                        'magnitude': 10,  # Font size
                        'unit': 'PT'  # Points
                    }
                },
                'fields': 'bold,underline,fontSize'
            }
        },
    ]

    handler.batch_put(document_id, total_loads_req)


    deductions =f"""
    
Factoring Vendor Fee 5%                                                  	${trucker.total_money} * 0.05 = ${trucker.factoring_fee}
Admin 5%                                                                    ${trucker.balance_after_factoring_fee} * 0.05 = ${trucker.admin_fee}
Drivers Credit                                                              ${trucker.balance_after_admin_fee} * 0.25 = ${trucker.pay}

												
Total for Payday Driver Credit 							${trucker.pay}

Balance							                                     ${trucker.balance}

To Be Paid {to_be_paid}

"""

    current_index = end_index - 1
    end_index = end_index + len(deductions)

    deductions_loads_req = [
        {
            'insertText': {
                'location': {
                    'index': current_index,  # Position to insert text
                },
                'text': deductions
            }
        },
        {
            'updateTextStyle': {
                'range': {
                    'startIndex': current_index,  # Start index of the text
                    'endIndex': end_index,  # End index of the text
                },
                'textStyle': {
                    'bold': False,
                    'underline': False,
                    'fontSize': {
                        'magnitude': 10,  # Font size
                        'unit': 'PT'  # Points
                    }
                },
                'fields': 'bold,underline,fontSize'
            }
        },
    ]

    handler.batch_put(document_id, deductions_loads_req)


def write_google_doc_truck_owner(trucker, pay_date_week_ending, to_be_paid, admin_expenses):
    handler = GoogleDocsApiHandler()
    document_name = f' PAY STATEMENT - Week Ending {pay_date_week_ending}'
    document_id = handler.create(document_name)



    # so index is calculated by the number of characters in strings
    driver_name = trucker.name
    pay_date_week_ending = pay_date_week_ending
    truck_name = trucker.truck

    company_name_header = "Mazarura Transport & Logistics LLC \n"
    secondary_name_driver = f"PAY STATEMENT - Week Ending {pay_date_week_ending} \n"
    truck = f"Truck {truck_name}"
    current_index = 1
    end_index = len(company_name_header)

    request_header = [
        {
            'insertText': {
                'location': {
                    'index': current_index,  # Position to insert text
                },
                'text': f'{company_name_header}'
            }
        },
        {
            'updateTextStyle': {
                'range': {
                    'startIndex': current_index,  # Start index of the text
                    'endIndex': end_index,  # End index of the text
                },
                'textStyle': {
                    'bold': True,
                    'underline': True,
                    'fontSize': {
                        'magnitude': 14,  # Font size
                        'unit': 'PT'  # Points
                    }
                },
                'fields': 'bold,underline,fontSize'
            }
        }
    ]

    current_index = end_index
    end_index = end_index + len(secondary_name_driver) + len(truck) + 1

    req_driver_pay_ending_and_truck_name = [
        {
            'insertText': {
                'location': {
                    'index': current_index,  # Position to insert text
                },
                'text': f'\n{secondary_name_driver}{truck}'
            }
        },
        {
            'updateTextStyle': {
                'range': {
                    'startIndex': current_index,  # Start index of the text
                    'endIndex': end_index,  # End index of the text
                },
                'textStyle': {
                    'bold': True,
                    'underline': False,
                    'fontSize': {
                        'magnitude': 11,  # Font size
                        'unit': 'PT'  # Points
                    }
                },
                'fields': 'bold,underline,fontSize'
            }
        },

    ]

    loads_header_text = """
    ----------------------------------------------------------------------------------------------------------------------------
    DATE 	   	Company  			RC/ LOAD				AMOUNT 
    ---------------------------------------------------------------------------------------------------------------------------- 
    """

    current_index = end_index
    end_index = end_index + len(loads_header_text)
    req_loads_header = [
        {
            'insertText': {
                'location': {
                    'index': current_index,  # Position to insert text
                },
                'text': f'\n{loads_header_text}'
            }
        },
        {
            'updateTextStyle': {
                'range': {
                    'startIndex': current_index,  # Start index of the text
                    'endIndex': end_index,  # End index of the text
                },
                'textStyle': {
                    'bold': True,
                    'underline': False,
                    'fontSize': {
                        'magnitude': 10,  # Font size
                        'unit': 'PT'  # Points
                    }
                },
                'fields': 'bold,underline,fontSize'
            }
        },
    ]

    handler = GoogleDocsApiHandler()
    handler.batch_put(document_id, request_header)
    handler.batch_put(document_id, req_driver_pay_ending_and_truck_name)
    handler.batch_put(document_id, req_loads_header)
    line = '\n'
    for trip in trucker.trips:
        if trip.truck_name == truck_name:
            line += f'{trip.date:<8} 	{trip.broker:<25}  		{trip.rate_con:<10}			{trip.rate:<7}\n'

    current_index = end_index
    end_index = end_index + len(line)

    loads_req = [
        {
            'insertText': {
                'location': {
                    'index': current_index,  # Position to insert text
                },
                'text': line
            }
        },
        {
            'updateTextStyle': {
                'range': {
                    'startIndex': current_index,  # Start index of the text
                    'endIndex': end_index,  # End index of the text
                },
                'textStyle': {
                    'bold': False,
                    'underline': False,
                    'fontSize': {
                        'magnitude': 10,  # Font size
                        'unit': 'PT'  # Points
                    }
                },
                'fields': 'bold,underline,fontSize'
            }
        },
    ]

    handler.batch_put(document_id, loads_req)
    total_revenue_lines = f"""
    ----------------------------------------------------------------------------------------------------------------------------
    Total for 100% Line Haul Revenue ${trucker.total_money}
    ----------------------------------------------------------------------------------------------------------------------------
    """

    current_index = end_index - 1
    end_index = end_index + len(total_revenue_lines)

    total_loads_req = [
        {
            'insertText': {
                'location': {
                    'index': current_index,  # Position to insert text
                },
                'text': total_revenue_lines
            }
        },
        {
            'updateTextStyle': {
                'range': {
                    'startIndex': current_index,  # Start index of the text
                    'endIndex': end_index,  # End index of the text
                },
                'textStyle': {
                    'bold': True,
                    'underline': False,
                    'fontSize': {
                        'magnitude': 10,  # Font size
                        'unit': 'PT'  # Points
                    }
                },
                'fields': 'bold,underline,fontSize'
            }
        },
    ]

    handler.batch_put(document_id, total_loads_req)
    deductions = f"""

    Factoring Vendor Fee 5%                                                  	${trucker.total_money} * 0.05 = ${trucker.factoring_fee}
    Admin 5%                                                                    ${trucker.balance_after_factoring_fee} * 0.05 = ${trucker.admin_fee}
    Drivers Credit                                                              ${trucker.balance_after_admin_fee} * 0.25 = ${trucker.pay}


    Total for Payday Driver Credit 							${trucker.pay}

    Balance							                        ${trucker.balance}


    """

    current_index = end_index - 1
    end_index = end_index + len(deductions)

    deductions_loads_req = [
        {
            'insertText': {
                'location': {
                    'index': current_index,  # Position to insert text
                },
                'text': deductions
            }
        },
        {
            'updateTextStyle': {
                'range': {
                    'startIndex': current_index,  # Start index of the text
                    'endIndex': end_index,  # End index of the text
                },
                'textStyle': {
                    'bold': False,
                    'underline': False,
                    'fontSize': {
                        'magnitude': 10,  # Font size
                        'unit': 'PT'  # Points
                    }
                },
                'fields': 'bold,underline,fontSize'
            }
        },
    ]

    handler.batch_put(document_id, deductions_loads_req)
    operating_expenses = f"""
       Less Operating Expenses                                              	${trucker.total_expenses} = ${round(trucker.balance - trucker.total_expenses, 2)} 
    """

    current_index = end_index - 1
    end_index = end_index + len(operating_expenses)

    operating_expenses_req = [
        {
            'insertText': {
                'location': {
                    'index': current_index,  # Position to insert text
                },
                'text': operating_expenses
            }
        },
        {
            'updateTextStyle': {
                'range': {
                    'startIndex': current_index,  # Start index of the text
                    'endIndex': end_index,  # End index of the text
                },
                'textStyle': {
                    'bold': True,
                    'underline': False,
                    'fontSize': {
                        'magnitude': 10,  # Font size
                        'unit': 'PT'  # Points
                    }
                },
                'fields': 'bold,underline,fontSize'
            }
        },
    ]

    handler.batch_put(document_id, operating_expenses_req)

    admin_expenses_str = f"""
    MT&L                    10%                                                 {trucker.balance} * 0.10 = ${admin_expenses.mtl_fee}
    Dispatch - Clement      10%                                                 {trucker.balance} * 0.10 = ${admin_expenses.dispatch_fee}
    Simba Admin - Rev        5%                                                 {trucker.balance} * 0.05 = ${admin_expenses.admin_fee}  
    Total Admin Expenses                                                            ${admin_expenses.total_admin}
    
    Payout                                                                      ${trucker.balance - trucker.total_expenses} - {admin_expenses.total_admin} = ${trucker.balance - (trucker.total_expenses + admin_expenses.total_admin)}
    ACH                                                                             $3.00
"""

    current_index = end_index - 1
    end_index = end_index + len(admin_expenses_str)

    admin_expenses_req = [
        {
            'insertText': {
                'location': {
                    'index': current_index,  # Position to insert text
                },
                'text': admin_expenses_str
            }
        },
        {
            'updateTextStyle': {
                'range': {
                    'startIndex': current_index,  # Start index of the text
                    'endIndex': end_index,  # End index of the text
                },
                'textStyle': {
                    'bold': False,
                    'underline': False,
                    'fontSize': {
                        'magnitude': 10,  # Font size
                        'unit': 'PT'  # Points
                    }
                },
                'fields': 'bold,underline,fontSize'
            }
        },
    ]

    handler.batch_put(document_id, admin_expenses_req)

    total_payday_for_contractor = trucker.balance - (trucker.total_expenses + admin_expenses.total_admin + 3)

    payout_date_str = f"""
    Total for Payday Contractor Credit                                              ${total_payday_for_contractor}
    
    To Be Paid ${to_be_paid}
    """

    current_index = end_index - 1
    end_index = end_index + len(payout_date_str)

    payout_req = [
        {
            'insertText': {
                'location': {
                    'index': current_index,  # Position to insert text
                },
                'text': payout_date_str
            }
        },
        {
            'updateTextStyle': {
                'range': {
                    'startIndex': current_index,  # Start index of the text
                    'endIndex': end_index,  # End index of the text
                },
                'textStyle': {
                    'bold': True,
                    'underline': False,
                    'fontSize': {
                        'magnitude': 10,  # Font size
                        'unit': 'PT'  # Points
                    }
                },
                'fields': 'bold,underline,fontSize'
            }
        },
    ]

    handler.batch_put(document_id, payout_req)


