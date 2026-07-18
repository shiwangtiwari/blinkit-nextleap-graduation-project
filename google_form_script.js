/**
 * BLINKIT CATEGORY DISCOVERY SURVEY
 *
 * How to use:
 * 1. Go to script.google.com
 * 2. Create a new project
 * 3. Paste this entire script
 * 4. Click Run > createSurveyForm
 * 5. Authorize when prompted
 * 6. The form URL will print in the execution log
 * 7. Open the form, click Settings > make it "Anyone with the link can respond"
 */

function createSurveyForm() {
  var form = FormApp.create("Blinkit Shopping Behavior Survey");
  form.setDescription(
    "Quick survey about how you shop on Blinkit and similar quick commerce apps. " +
    "Takes under 4 minutes. All responses are anonymous."
  );
  form.setConfirmationMessage("Thanks for your time.");
  form.setAllowResponseEdits(false);
  form.setLimitOneResponsePerUser(false);

  // --- Section 1: Who you are ---
  form.addSectionHeaderItem()
    .setTitle("About you")
    .setHelpText("Basic context so we can segment responses.");

  form.addMultipleChoiceItem()
    .setTitle("What is your age group?")
    .setChoiceValues(["18-24", "25-30", "31-35", "36-45", "46+"])
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle("Which city do you live in?")
    .setChoiceValues([
      "Delhi NCR (Delhi, Gurgaon, Noida, Faridabad, Ghaziabad)",
      "Mumbai / Navi Mumbai / Thane",
      "Bangalore",
      "Hyderabad",
      "Pune",
      "Chennai",
      "Kolkata",
      "Other metro",
      "Tier 2 city",
    ])
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle("Which quick commerce app do you use the most?")
    .setChoiceValues(["Blinkit", "Zepto", "Swiggy Instamart", "BigBasket BB Now", "Other"])
    .setRequired(true);

  // --- Section 2: Your shopping pattern ---
  form.addSectionHeaderItem()
    .setTitle("How you shop")
    .setHelpText("Think about your last month of orders.");

  form.addMultipleChoiceItem()
    .setTitle("How many times did you order on Blinkit (or your primary app) last month?")
    .setChoiceValues(["1-3 times", "4-6 times", "7-10 times", "11-15 times", "16+ times"])
    .setRequired(true);

  form.addCheckboxItem()
    .setTitle("Which categories do you buy regularly? (pick all that apply)")
    .setChoiceValues([
      "Groceries and staples (atta, rice, dal, oil)",
      "Dairy and bread (milk, eggs, curd, bread)",
      "Snacks and beverages",
      "Fruits and vegetables",
      "Personal care (shampoo, soap, skincare)",
      "Household cleaning (detergent, broom, wipes)",
      "Baby care",
      "Pet supplies",
      "Electronics and accessories",
      "Pharma and health",
      "Stationery",
    ])
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle("How do you usually start an order?")
    .setChoiceValues([
      "Search for a specific item I already know",
      "Open the reorder or past items section",
      "Browse the home screen and categories",
      "Use a saved list or cart",
    ])
    .setRequired(true);

  form.addScaleItem()
    .setTitle("What percentage of your orders are the same items as last time?")
    .setLabels("0% (always different)", "100% (always the same)")
    .setBounds(1, 5)
    .setRequired(true);

  // --- Section 3: Trying new categories ---
  form.addSectionHeaderItem()
    .setTitle("Trying new things")
    .setHelpText("By 'new category' we mean a type of product you have never bought on this app before. For example, buying pet food for the first time if you usually only buy groceries.");

  form.addMultipleChoiceItem()
    .setTitle("When did you last buy something from a category you had never tried on this app?")
    .setChoiceValues([
      "In the last week",
      "In the last month",
      "2-3 months ago",
      "More than 3 months ago",
      "I have never tried a new category",
    ])
    .setRequired(true);

  form.addCheckboxItem()
    .setTitle("What stops you from trying new categories on the app? (pick all that apply)")
    .setChoiceValues([
      "I do not know the app sells those products",
      "I do not trust the quality for that category",
      "Prices seem higher than where I usually buy",
      "I prefer buying that category in person (touch and feel)",
      "I already have a preferred store or app for that category",
      "The app never shows me relevant new products",
      "I have not thought about it, I just reorder what I need",
    ])
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle("If the app suggested products for a specific occasion (like 'weekend breakfast for the family' or 'monsoon essentials kit'), would you be more likely to try new categories?")
    .setChoiceValues([
      "Definitely yes",
      "Probably yes",
      "Not sure",
      "Probably not",
      "Definitely not",
    ])
    .setRequired(true);

  // --- Section 4: Trust and workarounds ---
  form.addSectionHeaderItem()
    .setTitle("Trust and alternatives");

  form.addCheckboxItem()
    .setTitle("Which categories do you NOT buy on quick commerce apps? (pick all that apply)")
    .setChoiceValues([
      "I buy everything on quick commerce",
      "Pet supplies",
      "Baby care",
      "Electronics",
      "Pharma and medicines",
      "Beauty and skincare",
      "Fresh meat or fish",
      "Specialty or imported food",
    ])
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle("Where do you buy those categories instead?")
    .setChoiceValues([
      "Amazon or Flipkart",
      "Local store or kirana",
      "Specialty store (pet shop, pharmacy, etc.)",
      "Another app (Nykaa, 1mg, Supertails, etc.)",
      "I buy everything on quick commerce already",
    ])
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle("What would make you most comfortable trying a new category on this app?")
    .setChoiceValues([
      "Easy returns if the product is not right",
      "Seeing ratings and reviews from other buyers",
      "A small trial size or sample pack",
      "Recommendation from someone I trust",
      "A discount on first purchase in that category",
    ])
    .setRequired(true);

  // --- Optional open text ---
  form.addParagraphTextItem()
    .setTitle("Anything else about how you discover or avoid new products on quick commerce? (optional)")
    .setRequired(false);

  Logger.log("Form created: " + form.getEditUrl());
  Logger.log("Share this URL for responses: " + form.getPublishedUrl());
}
