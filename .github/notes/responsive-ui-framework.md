# Responsive UI Framework

## Screen Size Breakpoints

```dart
class ScreenBreakpoints {
  static const double mobileMax = 600;
  static const double tabletMax = 1024;
  static const double desktopMin = 1025;
}
```

## Adaptive Layout System

### 1. Responsive Grid
```dart
class ResponsiveGrid extends StatelessWidget {
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        if (constraints.maxWidth < ScreenBreakpoints.mobileMax) {
          return MobileLayout();
        } else if (constraints.maxWidth < ScreenBreakpoints.tabletMax) {
          return TabletLayout();
        } else {
          return DesktopLayout();
        }
      },
    );
  }
}
```

### 2. Adaptive Navigation
```dart
class AdaptiveNavigation extends StatelessWidget {
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        if (constraints.maxWidth < ScreenBreakpoints.tabletMax) {
          return BottomNavigationBar(); // Mobile/small tablet
        } else {
          return NavigationRail(); // Large tablet/desktop
        }
      },
    );
  }
}
```

### 3. Map View Scaling
```dart
class ResponsiveMapView extends StatelessWidget {
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        double mapHeight = constraints.maxWidth < ScreenBreakpoints.mobileMax
            ? constraints.maxHeight * 0.6  // 60% on mobile
            : constraints.maxHeight * 0.8; // 80% on tablet+
        
        return Container(
          height: mapHeight,
          child: MapWidget(),
        );
      },
    );
  }
}
```

## Component Hierarchy

```
AppRoot
├── ResponsiveScaffold
│   ├── AdaptiveNavigation
│   ├── MainContent
│   │   ├── ResponsiveMapView
│   │   ├── AdaptiveControlPanel
│   │   └── ResponsiveDataDisplay
│   └── AdaptiveBottomSheet
```

## Orientation Handling

```dart
class OrientationAwareWidget extends StatelessWidget {
  Widget build(BuildContext context) {
    return OrientationBuilder(
      builder: (context, orientation) {
        if (orientation == Orientation.landscape) {
          return LandscapeLayout();
        } else {
          return PortraitLayout();
        }
      },
    );
  }
}
```
