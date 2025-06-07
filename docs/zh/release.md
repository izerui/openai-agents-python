# Release process
(发布流程)

The project follows a slightly modified version of semantic versioning using the form `0.Y.Z`. The leading `0` indicates the SDK is still evolving rapidly. Increment the components as follows:
(本项目采用略微修改的语义化版本控制，格式为`0.Y.Z`。开头的`0`表示SDK仍在快速演进中。版本号递增规则如下：)

## Minor (`Y`) versions
(次版本号(`Y`))

We will increase minor versions `Y` for **breaking changes** to any public interfaces that are not marked as beta. For example, going from `0.0.x` to `0.1.x` might include breaking changes.
(对于未标记为beta的公共接口的**破坏性变更**，我们将增加次版本号`Y`。例如，从`0.0.x`升级到`0.1.x`可能包含破坏性变更。)

If you don't want breaking changes, we recommend pinning to `0.0.x` versions in your project.
(如果不希望有破坏性变更，我们建议在项目中固定使用`0.0.x`版本。)

## Patch (`Z`) versions
(修订号(`Z`))

We will increment `Z` for non-breaking changes:
(我们将为以下非破坏性变更增加修订号`Z`：)

- Bug fixes
(错误修复)
- New features
(新功能)
- Changes to private interfaces
(私有接口变更)
- Updates to beta features
(beta功能更新)
