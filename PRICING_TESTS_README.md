# Pricing System Tests

This directory contains comprehensive test suites for the pricing and Stripe payment integration system.

## 🎯 Test Files Overview

### 1. `test_pricing_quick.py`

**Quick Essential Tests** - Run this before every deployment

- ✅ Authentication works
- ✅ Pricing plans are accessible
- ✅ Payment intent creation works
- ✅ Plan upgrade simulation works
- ✅ Plan verification works
- ✅ Usage stats work
- ✅ Downgrade works

### 2. `test_pricing_comprehensive.py`

**Full Integration Tests** - Run this for thorough validation

- ✅ All quick tests PLUS:
- ✅ Stripe test card scenarios (success, declined, processing errors)
- ✅ Error handling (invalid tokens, invalid plans)
- ✅ Edge cases and failure scenarios
- ✅ Complete payment flow simulation

### 3. `run_pricing_tests.py`

**Test Runner** - Easy way to run either test suite

## 🚀 How to Run Tests

### Prerequisites

1. **Start your FastAPI server:**

   ```bash
   cd server
   python main.py
   # Server should be running on http://localhost:8000
   ```

2. **Create a test user** (if not already exists):
   ```bash
   # Use your API or create via registration endpoint
   # Default test user: test@example.com / testpassword
   ```

### Quick Tests (Recommended before launch)

```bash
# Using the test runner (recommended)
python run_pricing_tests.py

# Or directly
python test_pricing_quick.py
```

### Comprehensive Tests (Full validation)

```bash
# Using the test runner
python run_pricing_tests.py --full

# Or directly
python test_pricing_comprehensive.py
```

### Custom Server URL

```bash
python run_pricing_tests.py --url http://your-server.com:8000
```

### Check Server Status Only

```bash
python run_pricing_tests.py --check-only
```

## 📋 Test Scenarios Covered

### ✅ Success Scenarios

- **Plan Upgrade**: User successfully upgrades to Professional plan
- **Payment Processing**: Stripe payment intent creation and confirmation
- **Plan Verification**: Upgraded plan is reflected in user subscription
- **Usage Stats**: Usage statistics correctly show new plan limits

### ❌ Failure Scenarios

- **Declined Cards**: Simulates Stripe card declined scenarios
- **Processing Errors**: Simulates payment processing failures
- **Insufficient Funds**: Tests insufficient funds scenarios
- **Network Errors**: Tests API error handling

### 🔒 Security Scenarios

- **Invalid Tokens**: Ensures invalid authentication is rejected
- **Invalid Plans**: Ensures invalid plan IDs are rejected
- **User Isolation**: Ensures users can only access their own data

## 🎨 Stripe Test Cards Used

The comprehensive tests use these Stripe test card numbers:

| Card Number        | Scenario           | Expected Result          |
| ------------------ | ------------------ | ------------------------ |
| `4242424242424242` | Success            | Payment succeeds         |
| `4000000000000002` | Declined           | Card declined            |
| `4000000000000341` | Processing Error   | Payment processing fails |
| `4000000000009995` | Insufficient Funds | Insufficient funds error |
| `4000000000000069` | Expired Card       | Card expired error       |
| `4000000000000127` | CVC Fail           | CVC check fails          |

## 📊 Expected Test Results

### ✅ All Tests Passing = Ready for Production

```
📊 QUICK TEST RESULTS
==================================================
Tests Passed: 7/7
Success Rate: 100.0%

🎉 ALL TESTS PASSED!
✅ Pricing system is ready for production!
```

### ❌ Some Tests Failing = Fix Issues First

```
📊 QUICK TEST RESULTS
==================================================
Tests Passed: 5/7
Success Rate: 71.4%

⚠️ 2 tests failed
❌ Fix issues before launching to production
```

## 🔧 Troubleshooting

### Common Issues

1. **Authentication Failed**

   - Create test user: `test@example.com` / `testpassword`
   - Or update credentials in test files

2. **Server Not Accessible**

   - Make sure FastAPI server is running
   - Check the URL and port (default: http://localhost:8000)

3. **Import Errors**

   - Install required packages: `pip install requests`

4. **Test Timeouts**
   - Check server performance
   - Increase timeout values in test files if needed

### Debug Mode

Add debug prints to test files if needed:

```python
print(f"Response: {response.status_code}")
print(f"Data: {response.text}")
```

## 🎉 Production Checklist

Before launching to production, ensure:

- [ ] ✅ Quick tests pass (100% success rate)
- [ ] ✅ Comprehensive tests pass (90%+ success rate)
- [ ] ✅ Stripe webhooks are configured
- [ ] ✅ Environment variables are set correctly
- [ ] ✅ Database backups are configured
- [ ] ✅ Monitoring is in place

## 📝 Notes

- Tests use **simulated** Stripe payments for safety
- No real charges are made during testing
- Test data is isolated from production data
- Comprehensive tests cover edge cases that may not occur in normal usage

---

**Ready to launch? Run the tests and make sure everything passes! 🚀**
