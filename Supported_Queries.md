# **=======================================================================================**
# 📘 NovaCart AI Assistant – Supported Query Catalogue
**=======================================================================================**


This document systematically describes **differents types of user queries** that the NovaCart AI Assistant can handle. Queries are classified based on **intent**, **complexity**, and **conversation flow**, including **multi-turn interactions** and **human escalation scenarios**.

**CASE A (single turn): Intent + Order ID both present.**
**CASE B (multi turn /fallback)  Order ID present but NO Intent.**   
**CASE C (multi turn /fallback): Intent Present but No Order ID**

----------------------------------------------------------------------------------------

## 1️⃣ Greeting & Session Initialization

>> These greeeting messeges occur when a user starts a new chat session.
### Bot Response
Bot:
"👋 Hi {username}! How can I assist you today?",
"😊 Welcome back, {username}! What would you like to do today?",
"🛒 Hey {username}! Ready to explore NovaCart?",
"✨ Hello {username}! I’m here to help you with your orders.",
"🙌 Hi {username}! How can I make your shopping easier today?"

>> These are generic Personalized greeting replies (handled by llm)
User: Hi
Bot: 👋 Hi ! How can I assist you today?
 
-----------------------------------------------------------------------

## 2️⃣ FAQ & Informational Queries (RAG-Based)

>> Handled using **Retrieval-Augmented Generation (RAG)** over NovaCart documents.

### Sample Queries
1. What does NovaCart do?  
2. What products do you sell?  
3. What is your return policy?  
4. How long does delivery take?  
5. How does refund work?  
6. What products does you company have for women's fashion?
7. Can you suggest me some products under electronics category?
8. what is the usp for your company?
9. How can we verify the authenticity of your products?
10. Tell me about your company's account and support.
11. What is your companies vision and target.
12. Can you tell me about your companies achievements.
13. I want to reset my password
14. What's the return policy on defective products

### Bot Response
Grounded answers from NovaCart documents.

---------------------------------------------------------------
#===============================================================================
**CASE A (single turn): Intent + Order ID both present.**
**CASE B (multi turn /fallback)  Order ID present but NO Intent.**   
**CASE C (multi turn /fallback): Intent Present but No Order ID**
#===============================================================================

## 3️⃣ Order Placement Queries (Single-Turn) (Case A)

### Sample Queries
1. Place an order for headphones  
2. Order 2 wireless headphones  
3. Buy a mirror  
4. I want to order shoes  
5. Order laptop stand  

### Bot Response : (Order summary ).
>> *For example*

User : Order 2 wireless headphones 
Bot: 
    🎉 YOUR ORDER PLACED SUCCESSFULLY 🎉
    🆔 Order ID: ORD-B6849A 📦 Product: wireless headphones 🔢 Quantity: 2
    You can track or return this order anytime.

## 5️⃣ Missing or Invalid Order Information (Fallback)

### Sample Queries
1. Place an order  
2. Order it  
3. Buy  
4. I want to purchase  
5. Order something  

### Bot Response: Asks user to specify product.
>> *For example*

User: I want to purchase
Bot: 
    Sure 👍 Add the Product to your cart.
    Example: Order 2 wireless headphones

--------------------------------------------------------

## 6️⃣ Order Tracking Queries
Handles all kinds of queries including single turn and fallback/multi-turn queries:-> 
(Valid Orders)
(Invalid Orders)
(CASE A)
(CASE B)
(CASE C)

### Sample Queries 
1. Track my order ORD-20eb75 
2. Where is my order?  
3. Check status of ORD-9876  
4. Has my order shipped?  
5. Track order  

### Bot Response: Order status + estimated delivery date.
>> *For example*

User: Track my order ORD-1234     **(Invalid order ID)**
Bot: ❌ I couldn’t find any order with ID ORD-1234 linked to your account.

User: Track my order ORD-20eb75 **(CASE A)**
Bot: 
    📦 STATUS OF YOUR ORDER
    🆔 Order ID: ORD-20eb75
    🛍️ Product: how many delivery attempts do you make
    🔢 Quantity: 1
    📅 Order Placed On: 16 Dec 2025
    📍 Status: RETURN_REQUESTED
    🚚 Estimated Delivery: 23 Dec 2025 – 25 Dec 2025

User: ORD-37682e        **(CASE B)**
Bot: 
    I found your order ID ORD-37682E.
    Please tell me exactly what you want me to do: (refer the below formate)
    • Track the ORD-XXXX
    • Return the ORD-XXXX
    • Raise a support ticket for ORD-XXXX with your concerns

User : Where is my order?  **(CASE C)**
Bot: 
    Sure 🙂 Please share your ORDER ID so I can track your order.
    Example: Track ORD-XXXX

----------------------------------------------------------------------------------

## 7️⃣ Return Requests
Handles all kinds of queries including single turn and fallback/multi-turn queries:-> 
(Valid Orders)
(Invalid Orders)
(CASE A)
(CASE B)
(CASE C)
(Duplicate Return --> Informs user that return is already initiated.)

### Sample Queries
1. Return ORD-37682e because it is damaged  
2. I want to return my order  
3. Wrong item received  
4. Product defective  
5. Initiate return  

### Bot Response: Return request confirmation with reason.
>> *For example*

User: Wrong item received under this order ORD-60022a
Bot: 
    ↩️ Return Request Raised Successfully
    📦 Order ID: ORD-106264 📝 Reason: Wrong item received
    Our team will process the return shortly.

User: Return ORD-37682e because it is damaged.    **Duplicate Return (Informs user that return is already initiated.)**
Bot: 
    ℹ️ A return request for Order ORD-37682e has already been initiated.
    Our team is currently processing it. You will be updated soon.

------------------------------------------------------------------------------

## 9️⃣ Support Ticket Queries

### Sample Queries
1. Raise a ticket for ORD-ddcf24 
2. I want to raise a ticket for ORD-60022a as it is not of good quality as expected

### Bot Response: Ticket created with Ticket ID.
Handles all kinds of queries including single turn and fallback/multi-turn queries:-> 
(Valid Orders)
(Invalid Orders)
(Human Escalation)
(CASE A)
(CASE B)
(CASE C)

>> *For example*
User: Raise a ticket for ORD-ddcf24
Bot:🎫 Support Ticket Created Successfully!
    🆔 Order ID: ORD-ddcf24 🎫 Ticket Number: TCK-59785B
    📝 Issue: ORD-ddcf24
    Our support team will review your request and get back to you soon.
 
## Human Escalation Queries

### Sample Queries
1. Talk to a human  
2. This is frustrating  
3. You are not helping  
4. Escalate this issue  
5. I need human support  

### Bot Response: Escalation confirmation with ticket number.
>>*For example*
User: Connect me to the human support
Bot: 👤 Your request has been escalated to a human support agent :
    🎫 Ticket Number: TCK-BFCFC5
    🎫 Escalated Reason: User Requested Human
    Our team will review the conversation and get back to you shortly.
    In case you don't get a call back in next 12hrs. Please contact our customer support team :
    📞 Phone: +91 98765 43210 (8 AM - 10 PM IST) 📧 Email: support@novacart.in

---------------------------------------------------------------------------------------------
## 9️⃣ Support Ticket Queries
### Bot Response: Tracks with order id and provides current status.
Handles all kinds of queries including single turn and fallback/multi-turn queries:-> 
(Valid Orders)
(Invalid Orders)
(CASE A)
(CASE B)
(CASE C)

>>*For example*
User: Please look into my order ORD-ddcf24, its not yet arrived
Bot: 📦 STATUS OF YOUR ORDER
    🆔 Order ID: ORD-ddcf24
    🛍️ Product: Groceries Essentials Combo
    🔢 Quantity: 1
    📅 Order Placed On: 17 Dec 2025
    📍 Status: RETURN_REQUESTED
    🚚 Estimated Delivery: 24 Dec 2025 – 26 Dec 2025

----------------------------------------------------------------------------------------------

## Unsupported / Out-of-Scope Queries

### Sample Queries
1. Tell me a joke  
2. What is the weather?  
3. Play music  
4. Explain quantum physics 

### Bot Response: Politely redirects to supported capabilities.
User:Tell me a joke
Bot: 
    I'd love to share a joke with you, but I'm a customer support assistant, and I'm here to help with your questions about NovaCart. Unfortunately, I don't have any jokes to share. Would you like to ask me something about NovaCart instead?

------------------------------------------------------------------------------------

## ✅ Summary

NovaCart AI Assistant supports:
- FAQ via RAG  
- Order placement (single & multi-turn)  
- Order tracking  
- Returns with validation  
- Support tickets  
- Human escalation  
- Confidence-aware handling  

This ensures a **robust, scalable, and intelligens of the BOT**.

----------------------------------------------------------------------------------------
