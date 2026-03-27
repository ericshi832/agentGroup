# Espresso & UIAutomator Patterns

Common patterns for Android instrumented UI testing.

---

## Espresso Core Patterns

### Basic Interactions

```kotlin
// Click
onView(withId(R.id.btn_submit)).perform(click())

// Type text
onView(withId(R.id.et_email))
    .perform(typeText("user@example.com"), closeSoftKeyboard())

// Clear and re-type
onView(withId(R.id.et_email))
    .perform(clearText(), typeText("new@example.com"), closeSoftKeyboard())

// Scroll and click (RecyclerView or ScrollView)
onView(withId(R.id.btn_submit)).perform(scrollTo(), click())

// Long click
onView(withId(R.id.item)).perform(longClick())

// Swipe
onView(withId(R.id.view_pager)).perform(swipeLeft())
```

### Assertions

```kotlin
// Is displayed
onView(withId(R.id.tv_title)).check(matches(isDisplayed()))

// Has text
onView(withId(R.id.tv_result)).check(matches(withText("Success")))

// Contains text (partial match)
onView(withId(R.id.tv_message)).check(matches(withText(containsString("Error"))))

// Is enabled / disabled
onView(withId(R.id.btn_submit)).check(matches(isEnabled()))
onView(withId(R.id.btn_submit)).check(matches(not(isEnabled())))

// Does not exist
onView(withId(R.id.pb_loading)).check(doesNotExist())

// Check EditText error
onView(withId(R.id.til_email))
    .check(matches(hasDescendant(withText("Invalid email"))))
```

### View Matchers — Choosing the Right One

```kotlin
// By ID (preferred — stable across text changes)
withId(R.id.btn_login)

// By text (use when ID not available)
withText("Login")
withText(R.string.login_button)   // Use string resource, not hardcoded

// By content description (accessibility label)
withContentDescription("Close dialog")

// By class
isAssignableFrom(EditText::class.java)

// Combination matchers
allOf(withId(R.id.btn_action), withText("Submit"), isDisplayed())

// Child of a parent
onView(allOf(withId(R.id.tv_label), isDescendantOfA(withId(R.id.card_user))))
```

### RecyclerView Testing

```kotlin
// Click item at position 0
onView(withId(R.id.rv_list))
    .perform(RecyclerViewActions.actionOnItemAtPosition<RecyclerView.ViewHolder>(0, click()))

// Scroll to position
onView(withId(R.id.rv_list))
    .perform(RecyclerViewActions.scrollToPosition<RecyclerView.ViewHolder>(10))

// Click item matching a text
onView(withId(R.id.rv_list))
    .perform(RecyclerViewActions.actionOnItem<RecyclerView.ViewHolder>(
        hasDescendant(withText("Product A")), click()
    ))

// Assert item count
onView(withId(R.id.rv_list)).check(matches(hasChildCount(3)))
```

### Dialog and Bottom Sheet

```kotlin
// Confirm dialog
onView(withText("OK")).inRoot(isDialog()).perform(click())

// Dismiss with back
pressBackUnconditionally()

// Check Snackbar
onView(withId(com.google.android.material.R.id.snackbar_text))
    .check(matches(withText("Saved successfully")))
```

### Navigation Testing

```kotlin
// With NavController
@Test
fun clickButton_navigatesToDetailFragment() {
    val navController = TestNavHostController(ApplicationProvider.getApplicationContext())

    val scenario = launchFragmentInContainer<HomeFragment>(
        themeResId = R.style.Theme_App
    ) {
        navController.setGraph(R.navigation.nav_graph)
        Navigation.setViewNavController(requireView(), navController)
    }

    onView(withId(R.id.btn_detail)).perform(click())
    assertThat(navController.currentDestination?.id).isEqualTo(R.id.detailFragment)
}
```

### Idling Resources (Async Operations)

```kotlin
// Register idling resource for OkHttp / Retrofit
@Before
fun registerIdlingResource() {
    IdlingRegistry.getInstance().register(OkHttp3IdlingResource.create("okhttp", okHttpClient))
}

@After
fun unregisterIdlingResource() {
    IdlingRegistry.getInstance().unregister(idlingResource)
}
```

---

## UIAutomator 2 Patterns

### Finding Elements

```kotlin
// By resource ID
device.findObject(By.res("com.example.app", "btn_login"))
device.findObject(UiSelector().resourceId("com.example.app:id/btn_login"))

// By text
device.findObject(By.text("Login"))
device.findObject(UiSelector().text("Login"))

// By content description
device.findObject(By.desc("Close"))

// By class
device.findObject(UiSelector().className("android.widget.EditText").instance(0))

// Chaining — child of parent
device.findObject(By.res("com.example.app", "card_user"))
      .findObject(By.clazz("android.widget.TextView"))
```

### Waiting for UI State

```kotlin
// Wait for element to appear (preferred over Thread.sleep)
device.wait(Until.hasObject(By.res(APP_PACKAGE, "tv_success")), 5_000L)

// Wait for text to change
device.wait(Until.findObject(By.res(APP_PACKAGE, "tv_status").text("Loaded")), 3_000L)

// Wait for element to disappear
device.wait(Until.gone(By.res(APP_PACKAGE, "pb_loading")), 5_000L)
```

### Scrolling

```kotlin
// Scroll down on a scrollable view
val scrollable = UiScrollable(UiSelector().scrollable(true))
scrollable.scrollToEnd(5)  // max 5 swipes

// Scroll to text
scrollable.scrollIntoView(UiSelector().text("Target Item"))

// Fling
scrollable.flingForward()
```

### Multi-Window / System UI

```kotlin
// Handle system permission dialog
val allowButton = device.findObject(UiSelector().text("Allow").packageName("com.android.permissioncontroller"))
if (allowButton.exists()) allowButton.click()

// Press system keys
device.pressBack()
device.pressHome()
device.openNotification()
```

---

## Test Data Management

### Fake / Stub Repository Pattern

```kotlin
class FakeAuthRepository : AuthRepository {
    var shouldSucceed = true
    var fakeUser = User(id = "1", email = "test@example.com")

    override suspend fun login(email: String, password: String): Result<User> {
        return if (shouldSucceed) Result.success(fakeUser)
        else Result.failure(AuthException.InvalidCredentials)
    }
}

// In test
@BindValue @JvmField
val authRepository: AuthRepository = FakeAuthRepository().also {
    it.shouldSucceed = false  // test failure scenario
}
```

### Test Fixtures (Kotlin objects)

```kotlin
object TestFixtures {
    val validUser = User(id = "1", email = "test@example.com", role = UserRole.USER)
    val adminUser = User(id = "2", email = "admin@example.com", role = UserRole.ADMIN)
    val expiredUser = User(id = "3", email = "expired@example.com", isActive = false)

    val loginRequest = LoginRequest(email = "test@example.com", password = "Password123!")
    val invalidLoginRequest = LoginRequest(email = "bad", password = "")
}
```

### Clearing App State Between Tests

```kotlin
@Before
fun clearAppData() {
    // Clear SharedPreferences
    InstrumentationRegistry.getInstrumentation().targetContext
        .getSharedPreferences("user_prefs", Context.MODE_PRIVATE)
        .edit().clear().commit()

    // Or via ADB (UIAutomator tests):
    // device.executeShellCommand("pm clear com.example.app")
}
```

---

## Common Test Failures and Fixes

| Failure | Cause | Fix |
|---------|-------|-----|
| `NoMatchingViewException` | View not visible or wrong ID | Use `get_ui_tree` or Layout Inspector to verify ID |
| `AmbiguousViewMatcherException` | Multiple views match | Add more specific matchers (`allOf`, `isDisplayed()`) |
| `PerformException`: view not clickable | View behind overlay or disabled | Wait for overlay to dismiss; verify `isEnabled()` first |
| Flaky: sometimes passes, sometimes fails | Race condition on async load | Replace `Thread.sleep` with `waitFor` / `IdlingResource` |
| Test passes locally, fails on CI | Different screen size or API level | Use resource IDs, not coordinates; test on API 26-34 range |
| `ActivityNotFoundException` | Wrong package/Activity name | Run `mcp__android__get_current_activity` to verify |
