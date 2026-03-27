# Android Testing Strategies

---

## Test Pyramid for Android

```
         ┌──────────┐
         │  E2E UI  │  10%  UIAutomator 2 / MCP Android
         │   Tests  │
         ├──────────┤
         │  Integr. │  20%  Espresso, AndroidJUnit4,
         │  Tests   │       Instrumented Tests
         ├──────────┤
         │   Unit   │  70%  JUnit 4/5, Mockito,
         │   Tests  │       Robolectric
         └──────────┘
```

### Distribution Guidelines

| Layer | Ratio | Execution Speed | Reliability | Cost |
|-------|-------|-----------------|-------------|------|
| Unit | 70% | Fast (<1s each) | High | Low |
| Integration (Instrumented) | 20% | Slow (emulator required) | Medium | Medium |
| E2E / UI | 10% | Slowest | Lower (flakiness) | High |

**Rule of thumb**: If a test can be a unit test, make it a unit test.

---

## Coverage Targets by Project Phase

| Phase | Line | Branch | Method | Notes |
|-------|------|--------|--------|-------|
| Prototype / MVP | 40% | 30% | 50% | Focus on happy path |
| Beta | 60% | 50% | 65% | Add error handling tests |
| Production | 70% | 60% | 75% | Standard threshold |
| Enterprise / Regulated | 85% | 75% | 90% | Finance, Health, Auth critical paths |

**Priority order**: Data Layer > Domain Layer > Presentation Layer > UI

---

## Unit Testing

### What to Unit Test

```
✅ ViewModels          — state logic, LiveData/StateFlow emissions
✅ Use Cases           — business rules, input validation
✅ Repositories        — data transformation, error mapping
✅ Utility classes     — date formatting, string parsing, calculations
✅ Mappers             — DTO ↔ domain model conversion
❌ Activities/Fragments — use Espresso for these
❌ Simple data classes  — getters/setters don't need tests
```

### JUnit 4 Structure

```kotlin
@RunWith(JUnit4::class)
class LoginViewModelTest {

    // Mocks
    @Mock private lateinit var authRepository: AuthRepository
    @Mock private lateinit var userPreferences: UserPreferences

    // System Under Test
    private lateinit var sut: LoginViewModel

    @Before
    fun setUp() {
        MockitoAnnotations.openMocks(this)
        sut = LoginViewModel(authRepository, userPreferences)
    }

    @Test
    fun `login with valid credentials emits Success state`() {
        // Arrange
        whenever(authRepository.login("user@example.com", "Pass123!"))
            .thenReturn(Result.success(User(id = "1", email = "user@example.com")))

        // Act
        sut.login("user@example.com", "Pass123!")

        // Assert
        assertThat(sut.uiState.value).isInstanceOf(LoginUiState.Success::class.java)
    }

    @Test
    fun `login with wrong password emits Error state`() {
        whenever(authRepository.login(any(), any()))
            .thenReturn(Result.failure(AuthException.InvalidCredentials))

        sut.login("user@example.com", "wrong")

        assertThat(sut.uiState.value).isInstanceOf(LoginUiState.Error::class.java)
    }
}
```

### Testing Coroutines

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
class LoginViewModelTest {

    @get:Rule
    val coroutineRule = MainCoroutineRule()  // replaces Dispatchers.Main

    @Test
    fun `login shows loading then success`() = runTest {
        // Arrange
        whenever(authRepository.login(any(), any())).coAnswers {
            delay(100)
            Result.success(fakeUser)
        }

        // Act
        sut.login("user@example.com", "pass")
        advanceTimeBy(50)

        // Assert loading
        assertThat(sut.uiState.value).isEqualTo(LoginUiState.Loading)

        advanceUntilIdle()

        // Assert success
        assertThat(sut.uiState.value).isInstanceOf(LoginUiState.Success::class.java)
    }
}
```

### Robolectric for Android Framework Classes

```kotlin
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class NotificationHelperTest {

    private lateinit var context: Context
    private lateinit var sut: NotificationHelper

    @Before
    fun setUp() {
        context = ApplicationProvider.getApplicationContext()
        sut = NotificationHelper(context)
    }

    @Test
    fun `createNotification returns valid notification`() {
        val notification = sut.createNotification("Title", "Body")
        assertThat(notification.extras.getString("android.title")).isEqualTo("Title")
    }
}
```

---

## Integration Testing (Instrumented)

### Espresso for Activity/Fragment

```kotlin
@RunWith(AndroidJUnit4::class)
class LoginActivityTest {

    @get:Rule
    val activityRule = ActivityScenarioRule(LoginActivity::class.java)

    @Test
    fun typeEmail_andClickLogin_navigatesToHome() {
        onView(withId(R.id.et_email))
            .perform(typeText("test@example.com"), closeSoftKeyboard())
        onView(withId(R.id.et_password))
            .perform(typeText("Password123!"), closeSoftKeyboard())
        onView(withId(R.id.btn_login)).perform(click())

        // Verify navigation
        onView(withId(R.id.fragment_home)).check(matches(isDisplayed()))
    }

    @Test
    fun emptyEmail_showsValidationError() {
        onView(withId(R.id.btn_login)).perform(click())
        onView(withId(R.id.til_email))
            .check(matches(hasDescendant(withText("Email is required"))))
    }
}
```

### Hilt Dependency Injection in Tests

```kotlin
@HiltAndroidTest
@RunWith(AndroidJUnit4::class)
class LoginActivityTest {

    @get:Rule(order = 0)
    val hiltRule = HiltAndroidRule(this)

    @get:Rule(order = 1)
    val activityRule = ActivityScenarioRule(LoginActivity::class.java)

    @BindValue @JvmField
    val fakeAuthRepository: AuthRepository = FakeAuthRepository()

    @Before
    fun setUp() {
        hiltRule.inject()
    }
}
```

---

## UI/E2E Testing

### UIAutomator 2 Black-box Flow

```kotlin
@RunWith(AndroidJUnit4::class)
class CheckoutFlowTest {

    private lateinit var device: UiDevice

    @Before
    fun setUp() {
        device = UiDevice.getInstance(InstrumentationRegistry.getInstrumentation())
        device.pressHome()
        launchApp(APP_PACKAGE)
    }

    @Test
    fun fullCheckoutFlow_completesSuccessfully() {
        // Login
        device.findObject(UiSelector().resourceId("$APP_PACKAGE:id/et_email"))
            .setText("test@example.com")
        device.findObject(UiSelector().resourceId("$APP_PACKAGE:id/btn_login")).click()
        device.wait(Until.hasObject(By.res(APP_PACKAGE, "rv_products")), 3_000L)

        // Add to cart
        device.findObject(By.res(APP_PACKAGE, "btn_add_to_cart")).click()

        // Checkout
        device.findObject(By.res(APP_PACKAGE, "btn_checkout")).click()
        device.wait(Until.hasObject(By.text("Order Confirmed")), 5_000L)

        assertNotNull(device.findObject(By.text("Order Confirmed")))
    }
}
```

---

## CI/CD Considerations

### Unit Tests — Run on Every PR

```yaml
- name: Run unit tests
  run: ./gradlew test

- name: Generate coverage report
  run: ./gradlew jacocoTestReport

- name: Check coverage threshold
  run: python scripts/coverage_analyzer.py \
         build/reports/jacoco/test/jacocoTestReport.xml \
         --threshold 70 --strict
```

### Instrumented Tests — Run on Emulator

```yaml
- name: Run instrumented tests
  uses: reactivecircus/android-emulator-runner@v2
  with:
    api-level: 34
    target: google_apis
    arch: x86_64
    script: ./gradlew connectedAndroidTest
```

### Flaky Test Handling

```
1. Never retry flaky tests silently — fix root cause
2. Common flaky causes:
   - Sleep/delay instead of waiting for UI condition → use waitFor()
   - Hardcoded coordinates → use resource IDs
   - Shared state between tests → use @Before/@After cleanup
3. Mark known-flaky tests with @FlakyTest and track in issues
```

---

## Testing Anti-patterns

| Anti-pattern | Problem | Fix |
|-------------|---------|-----|
| Testing implementation details | Tests break on refactor | Test behavior, not internals |
| No setup/teardown | State leaks between tests | Use `@Before` / `@After` |
| `Thread.sleep()` in UI tests | Flakiness, slow | Use `waitFor()` / Espresso `IdlingResource` |
| Testing Android framework classes without Robolectric | JVM crash | Add `@RunWith(RobolectricTestRunner::class)` |
| Single monolithic test method | Hard to debug failures | One assertion focus per test |
| Mocking everything | Tests pass but prod breaks | Only mock external boundaries |
