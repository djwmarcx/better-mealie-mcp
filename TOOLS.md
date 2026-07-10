# Better Mealie MCP — Tool Reference

**259 tools**, auto-generated from Mealie's OpenAPI spec. Every endpoint included, none excluded.

## `admin` (38)

| tool | method | path |
|------|--------|------|
| `create_admin_backups` | POST | `/api/admin/backups` |
| `create_admin_backups_by_file_name_restore` | POST | `/api/admin/backups/{file_name}/restore` |
| `create_admin_backups_upload` | POST | `/api/admin/backups/upload` |
| `create_admin_debug_openai_by_provider` | POST | `/api/admin/debug/openai/{provider_id}` |
| `create_admin_email` | POST | `/api/admin/email` |
| `create_admin_groups` | POST | `/api/admin/groups` |
| `create_admin_groups_by_group_ai_providers_providers` | POST | `/api/admin/groups/{group_id}/ai-providers/providers` |
| `create_admin_households` | POST | `/api/admin/households` |
| `create_admin_maintenance_clean_images` | POST | `/api/admin/maintenance/clean/images` |
| `create_admin_maintenance_clean_recipe_folders` | POST | `/api/admin/maintenance/clean/recipe-folders` |
| `create_admin_maintenance_clean_temp` | POST | `/api/admin/maintenance/clean/temp` |
| `create_admin_users` | POST | `/api/admin/users` |
| `create_admin_users_password_reset_token` | POST | `/api/admin/users/password-reset-token` |
| `create_admin_users_unlock` | POST | `/api/admin/users/unlock` |
| `delete_admin_backups_by_file_name` | DELETE | `/api/admin/backups/{file_name}` |
| `delete_admin_groups_by_group_ai_providers_providers_by_p` | DELETE | `/api/admin/groups/{group_id}/ai-providers/providers/{provider_id}` |
| `delete_admin_groups_by_item` | DELETE | `/api/admin/groups/{item_id}` |
| `delete_admin_households_by_item` | DELETE | `/api/admin/households/{item_id}` |
| `delete_admin_users_by_item` | DELETE | `/api/admin/users/{item_id}` |
| `get_admin_backups_by_file_name` | GET | `/api/admin/backups/{file_name}` |
| `get_admin_groups_by_group_ai_providers_providers_by_prov` | GET | `/api/admin/groups/{group_id}/ai-providers/providers/{provider_id}` |
| `get_admin_groups_by_item` | GET | `/api/admin/groups/{item_id}` |
| `get_admin_households_by_item` | GET | `/api/admin/households/{item_id}` |
| `get_admin_users_by_item` | GET | `/api/admin/users/{item_id}` |
| `list_admin_about` | GET | `/api/admin/about` |
| `list_admin_about_check` | GET | `/api/admin/about/check` |
| `list_admin_about_statistics` | GET | `/api/admin/about/statistics` |
| `list_admin_backups` | GET | `/api/admin/backups` |
| `list_admin_email` | GET | `/api/admin/email` |
| `list_admin_groups` | GET | `/api/admin/groups` |
| `list_admin_households` | GET | `/api/admin/households` |
| `list_admin_maintenance` | GET | `/api/admin/maintenance` |
| `list_admin_maintenance_storage` | GET | `/api/admin/maintenance/storage` |
| `list_admin_users` | GET | `/api/admin/users` |
| `update_admin_groups_by_group_ai_providers_providers_by_p` | PUT | `/api/admin/groups/{group_id}/ai-providers/providers/{provider_id}` |
| `update_admin_groups_by_item` | PUT | `/api/admin/groups/{item_id}` |
| `update_admin_households_by_item` | PUT | `/api/admin/households/{item_id}` |
| `update_admin_users_by_item` | PUT | `/api/admin/users/{item_id}` |

## `app` (3)

| tool | method | path |
|------|--------|------|
| `list_app_about` | GET | `/api/app/about` |
| `list_app_about_startup_info` | GET | `/api/app/about/startup-info` |
| `list_app_about_theme` | GET | `/api/app/about/theme` |

## `auth` (5)

| tool | method | path |
|------|--------|------|
| `create_auth_logout` | POST | `/api/auth/logout` |
| `create_auth_token` | POST | `/api/auth/token` |
| `list_auth_oauth` | GET | `/api/auth/oauth` |
| `list_auth_oauth_callback` | GET | `/api/auth/oauth/callback` |
| `list_auth_refresh` | GET | `/api/auth/refresh` |

## `comments` (5)

| tool | method | path |
|------|--------|------|
| `create_comments` | POST | `/api/comments` |
| `delete_comments_by_item` | DELETE | `/api/comments/{item_id}` |
| `get_comments_by_item` | GET | `/api/comments/{item_id}` |
| `list_comments` | GET | `/api/comments` |
| `update_comments_by_item` | PUT | `/api/comments/{item_id}` |

## `explore` (15)

| tool | method | path |
|------|--------|------|
| `get_explore_groups_by_group_slug_cookbooks_by_item` | GET | `/api/explore/groups/{group_slug}/cookbooks/{item_id}` |
| `get_explore_groups_by_group_slug_foods_by_item` | GET | `/api/explore/groups/{group_slug}/foods/{item_id}` |
| `get_explore_groups_by_group_slug_households_by_household` | GET | `/api/explore/groups/{group_slug}/households/{household_slug}` |
| `get_explore_groups_by_group_slug_organizers_categories_b` | GET | `/api/explore/groups/{group_slug}/organizers/categories/{item_id}` |
| `get_explore_groups_by_group_slug_organizers_tags_by_item` | GET | `/api/explore/groups/{group_slug}/organizers/tags/{item_id}` |
| `get_explore_groups_by_group_slug_organizers_tools_by_ite` | GET | `/api/explore/groups/{group_slug}/organizers/tools/{item_id}` |
| `get_explore_groups_by_group_slug_recipes_by_recipe_slug` | GET | `/api/explore/groups/{group_slug}/recipes/{recipe_slug}` |
| `list_explore_groups_by_group_slug_cookbooks` | GET | `/api/explore/groups/{group_slug}/cookbooks` |
| `list_explore_groups_by_group_slug_foods` | GET | `/api/explore/groups/{group_slug}/foods` |
| `list_explore_groups_by_group_slug_households` | GET | `/api/explore/groups/{group_slug}/households` |
| `list_explore_groups_by_group_slug_organizers_categories` | GET | `/api/explore/groups/{group_slug}/organizers/categories` |
| `list_explore_groups_by_group_slug_organizers_tags` | GET | `/api/explore/groups/{group_slug}/organizers/tags` |
| `list_explore_groups_by_group_slug_organizers_tools` | GET | `/api/explore/groups/{group_slug}/organizers/tools` |
| `list_explore_groups_by_group_slug_recipes` | GET | `/api/explore/groups/{group_slug}/recipes` |
| `list_explore_groups_by_group_slug_recipes_suggestions` | GET | `/api/explore/groups/{group_slug}/recipes/suggestions` |

## `foods` (6)

| tool | method | path |
|------|--------|------|
| `create_foods` | POST | `/api/foods` |
| `delete_foods_by_item` | DELETE | `/api/foods/{item_id}` |
| `get_foods_by_item` | GET | `/api/foods/{item_id}` |
| `list_foods` | GET | `/api/foods` |
| `update_foods_by_item` | PUT | `/api/foods/{item_id}` |
| `update_foods_merge` | PUT | `/api/foods/merge` |

## `groups` (26)

| tool | method | path |
|------|--------|------|
| `create_groups_ai_providers_providers` | POST | `/api/groups/ai-providers/providers` |
| `create_groups_labels` | POST | `/api/groups/labels` |
| `create_groups_migrations` | POST | `/api/groups/migrations` |
| `create_groups_seeders_foods` | POST | `/api/groups/seeders/foods` |
| `create_groups_seeders_labels` | POST | `/api/groups/seeders/labels` |
| `create_groups_seeders_units` | POST | `/api/groups/seeders/units` |
| `delete_groups_ai_providers_providers_by_provider` | DELETE | `/api/groups/ai-providers/providers/{provider_id}` |
| `delete_groups_labels_by_item` | DELETE | `/api/groups/labels/{item_id}` |
| `delete_groups_reports_by_item` | DELETE | `/api/groups/reports/{item_id}` |
| `get_groups_ai_providers_providers_by_provider` | GET | `/api/groups/ai-providers/providers/{provider_id}` |
| `get_groups_households_by_household_slug` | GET | `/api/groups/households/{household_slug}` |
| `get_groups_labels_by_item` | GET | `/api/groups/labels/{item_id}` |
| `get_groups_members_by_username_or` | GET | `/api/groups/members/{username_or_id}` |
| `get_groups_reports_by_item` | GET | `/api/groups/reports/{item_id}` |
| `list_groups_ai_providers_settings` | GET | `/api/groups/ai-providers/settings` |
| `list_groups_households` | GET | `/api/groups/households` |
| `list_groups_labels` | GET | `/api/groups/labels` |
| `list_groups_members` | GET | `/api/groups/members` |
| `list_groups_preferences` | GET | `/api/groups/preferences` |
| `list_groups_reports` | GET | `/api/groups/reports` |
| `list_groups_self` | GET | `/api/groups/self` |
| `list_groups_storage` | GET | `/api/groups/storage` |
| `update_groups_ai_providers_providers_by_provider` | PUT | `/api/groups/ai-providers/providers/{provider_id}` |
| `update_groups_ai_providers_settings` | PUT | `/api/groups/ai-providers/settings` |
| `update_groups_labels_by_item` | PUT | `/api/groups/labels/{item_id}` |
| `update_groups_preferences` | PUT | `/api/groups/preferences` |

## `households` (64)

| tool | method | path |
|------|--------|------|
| `create_households_cookbooks` | POST | `/api/households/cookbooks` |
| `create_households_events_notifications` | POST | `/api/households/events/notifications` |
| `create_households_events_notifications_by_item_test` | POST | `/api/households/events/notifications/{item_id}/test` |
| `create_households_invitations` | POST | `/api/households/invitations` |
| `create_households_invitations_email` | POST | `/api/households/invitations/email` |
| `create_households_mealplans` | POST | `/api/households/mealplans` |
| `create_households_mealplans_random` | POST | `/api/households/mealplans/random` |
| `create_households_mealplans_rules` | POST | `/api/households/mealplans/rules` |
| `create_households_recipe_actions` | POST | `/api/households/recipe-actions` |
| `create_households_recipe_actions_by_item_trigger_by_reci` | POST | `/api/households/recipe-actions/{item_id}/trigger/{recipe_slug}` |
| `create_households_shopping_items` | POST | `/api/households/shopping/items` |
| `create_households_shopping_items_create_bulk` | POST | `/api/households/shopping/items/create-bulk` |
| `create_households_shopping_lists` | POST | `/api/households/shopping/lists` |
| `create_households_shopping_lists_by_item_recipe` | POST | `/api/households/shopping/lists/{item_id}/recipe` |
| `create_households_shopping_lists_by_item_recipe_by_rec_2` | POST | `/api/households/shopping/lists/{item_id}/recipe/{recipe_id}/delete` |
| `create_households_shopping_lists_by_item_recipe_by_recip` | POST | `/api/households/shopping/lists/{item_id}/recipe/{recipe_id}` |
| `create_households_webhooks` | POST | `/api/households/webhooks` |
| `create_households_webhooks_by_item_test` | POST | `/api/households/webhooks/{item_id}/test` |
| `create_households_webhooks_rerun` | POST | `/api/households/webhooks/rerun` |
| `delete_households_cookbooks_by_item` | DELETE | `/api/households/cookbooks/{item_id}` |
| `delete_households_events_notifications_by_item` | DELETE | `/api/households/events/notifications/{item_id}` |
| `delete_households_mealplans_by_item` | DELETE | `/api/households/mealplans/{item_id}` |
| `delete_households_mealplans_rules_by_item` | DELETE | `/api/households/mealplans/rules/{item_id}` |
| `delete_households_recipe_actions_by_item` | DELETE | `/api/households/recipe-actions/{item_id}` |
| `delete_households_shopping_items` | DELETE | `/api/households/shopping/items` |
| `delete_households_shopping_items_by_item` | DELETE | `/api/households/shopping/items/{item_id}` |
| `delete_households_shopping_lists_by_item` | DELETE | `/api/households/shopping/lists/{item_id}` |
| `delete_households_webhooks_by_item` | DELETE | `/api/households/webhooks/{item_id}` |
| `get_households_cookbooks_by_item` | GET | `/api/households/cookbooks/{item_id}` |
| `get_households_events_notifications_by_item` | GET | `/api/households/events/notifications/{item_id}` |
| `get_households_mealplans_by_item` | GET | `/api/households/mealplans/{item_id}` |
| `get_households_mealplans_rules_by_item` | GET | `/api/households/mealplans/rules/{item_id}` |
| `get_households_recipe_actions_by_item` | GET | `/api/households/recipe-actions/{item_id}` |
| `get_households_self_recipes_by_recipe_slug` | GET | `/api/households/self/recipes/{recipe_slug}` |
| `get_households_shopping_items_by_item` | GET | `/api/households/shopping/items/{item_id}` |
| `get_households_shopping_lists_by_item` | GET | `/api/households/shopping/lists/{item_id}` |
| `get_households_webhooks_by_item` | GET | `/api/households/webhooks/{item_id}` |
| `list_households_cookbooks` | GET | `/api/households/cookbooks` |
| `list_households_events_notifications` | GET | `/api/households/events/notifications` |
| `list_households_invitations` | GET | `/api/households/invitations` |
| `list_households_mealplans` | GET | `/api/households/mealplans` |
| `list_households_mealplans_rules` | GET | `/api/households/mealplans/rules` |
| `list_households_mealplans_today` | GET | `/api/households/mealplans/today` |
| `list_households_members` | GET | `/api/households/members` |
| `list_households_preferences` | GET | `/api/households/preferences` |
| `list_households_recipe_actions` | GET | `/api/households/recipe-actions` |
| `list_households_self` | GET | `/api/households/self` |
| `list_households_shopping_items` | GET | `/api/households/shopping/items` |
| `list_households_shopping_lists` | GET | `/api/households/shopping/lists` |
| `list_households_statistics` | GET | `/api/households/statistics` |
| `list_households_webhooks` | GET | `/api/households/webhooks` |
| `update_households_cookbooks` | PUT | `/api/households/cookbooks` |
| `update_households_cookbooks_by_item` | PUT | `/api/households/cookbooks/{item_id}` |
| `update_households_events_notifications_by_item` | PUT | `/api/households/events/notifications/{item_id}` |
| `update_households_mealplans_by_item` | PUT | `/api/households/mealplans/{item_id}` |
| `update_households_mealplans_rules_by_item` | PUT | `/api/households/mealplans/rules/{item_id}` |
| `update_households_permissions` | PUT | `/api/households/permissions` |
| `update_households_preferences` | PUT | `/api/households/preferences` |
| `update_households_recipe_actions_by_item` | PUT | `/api/households/recipe-actions/{item_id}` |
| `update_households_shopping_items` | PUT | `/api/households/shopping/items` |
| `update_households_shopping_items_by_item` | PUT | `/api/households/shopping/items/{item_id}` |
| `update_households_shopping_lists_by_item` | PUT | `/api/households/shopping/lists/{item_id}` |
| `update_households_shopping_lists_by_item_label_settings` | PUT | `/api/households/shopping/lists/{item_id}/label-settings` |
| `update_households_webhooks_by_item` | PUT | `/api/households/webhooks/{item_id}` |

## `media` (5)

| tool | method | path |
|------|--------|------|
| `get_media_recipes_by_recipe_assets_by_file_name` | GET | `/api/media/recipes/{recipe_id}/assets/{file_name}` |
| `get_media_recipes_by_recipe_images_by_file_name` | GET | `/api/media/recipes/{recipe_id}/images/{file_name}` |
| `get_media_recipes_by_recipe_images_timeline_by_timeline` | GET | `/api/media/recipes/{recipe_id}/images/timeline/{timeline_event_id}/{file_name}` |
| `get_media_users_by_user_by_file_name` | GET | `/api/media/users/{user_id}/{file_name}` |
| `list_media_docker_validate_txt` | GET | `/api/media/docker/validate.txt` |

## `organizers` (20)

| tool | method | path |
|------|--------|------|
| `create_organizers_categories` | POST | `/api/organizers/categories` |
| `create_organizers_tags` | POST | `/api/organizers/tags` |
| `create_organizers_tools` | POST | `/api/organizers/tools` |
| `delete_organizers_categories_by_item` | DELETE | `/api/organizers/categories/{item_id}` |
| `delete_organizers_tags_by_item` | DELETE | `/api/organizers/tags/{item_id}` |
| `delete_organizers_tools_by_item` | DELETE | `/api/organizers/tools/{item_id}` |
| `get_organizers_categories_by_item` | GET | `/api/organizers/categories/{item_id}` |
| `get_organizers_categories_slug_by_category_slug` | GET | `/api/organizers/categories/slug/{category_slug}` |
| `get_organizers_tags_by_item` | GET | `/api/organizers/tags/{item_id}` |
| `get_organizers_tags_slug_by_tag_slug` | GET | `/api/organizers/tags/slug/{tag_slug}` |
| `get_organizers_tools_by_item` | GET | `/api/organizers/tools/{item_id}` |
| `get_organizers_tools_slug_by_tool_slug` | GET | `/api/organizers/tools/slug/{tool_slug}` |
| `list_organizers_categories` | GET | `/api/organizers/categories` |
| `list_organizers_categories_empty` | GET | `/api/organizers/categories/empty` |
| `list_organizers_tags` | GET | `/api/organizers/tags` |
| `list_organizers_tags_empty` | GET | `/api/organizers/tags/empty` |
| `list_organizers_tools` | GET | `/api/organizers/tools` |
| `update_organizers_categories_by_item` | PUT | `/api/organizers/categories/{item_id}` |
| `update_organizers_tags_by_item` | PUT | `/api/organizers/tags/{item_id}` |
| `update_organizers_tools_by_item` | PUT | `/api/organizers/tools/{item_id}` |

## `parser` (2)

| tool | method | path |
|------|--------|------|
| `create_parser_ingredient` | POST | `/api/parser/ingredient` |
| `create_parser_ingredients` | POST | `/api/parser/ingredients` |

## `recipes` (42)

| tool | method | path |
|------|--------|------|
| `create_recipes` | POST | `/api/recipes` |
| `create_recipes_bulk_actions_categorize` | POST | `/api/recipes/bulk-actions/categorize` |
| `create_recipes_bulk_actions_delete` | POST | `/api/recipes/bulk-actions/delete` |
| `create_recipes_bulk_actions_export` | POST | `/api/recipes/bulk-actions/export` |
| `create_recipes_bulk_actions_settings` | POST | `/api/recipes/bulk-actions/settings` |
| `create_recipes_bulk_actions_tag` | POST | `/api/recipes/bulk-actions/tag` |
| `create_recipes_by_slug_assets` | POST | `/api/recipes/{slug}/assets` |
| `create_recipes_by_slug_duplicate` | POST | `/api/recipes/{slug}/duplicate` |
| `create_recipes_by_slug_image` | POST | `/api/recipes/{slug}/image` |
| `create_recipes_create_html_or_json` | POST | `/api/recipes/create/html-or-json` |
| `create_recipes_create_html_or_json_stream` | POST | `/api/recipes/create/html-or-json/stream` |
| `create_recipes_create_image` | POST | `/api/recipes/create/image` |
| `create_recipes_create_url` | POST | `/api/recipes/create/url` |
| `create_recipes_create_url_bulk` | POST | `/api/recipes/create/url/bulk` |
| `create_recipes_create_url_stream` | POST | `/api/recipes/create/url/stream` |
| `create_recipes_create_zip` | POST | `/api/recipes/create/zip` |
| `create_recipes_test_scrape_url` | POST | `/api/recipes/test-scrape-url` |
| `create_recipes_timeline_events` | POST | `/api/recipes/timeline/events` |
| `delete_recipes_bulk_actions_export_purge` | DELETE | `/api/recipes/bulk-actions/export/purge` |
| `delete_recipes_by_slug` | DELETE | `/api/recipes/{slug}` |
| `delete_recipes_by_slug_image` | DELETE | `/api/recipes/{slug}/image` |
| `delete_recipes_timeline_events_by_item` | DELETE | `/api/recipes/timeline/events/{item_id}` |
| `get_recipes_by_slug` | GET | `/api/recipes/{slug}` |
| `get_recipes_shared_by_token` | GET | `/api/recipes/shared/{token_id}` |
| `get_recipes_timeline_events_by_item` | GET | `/api/recipes/timeline/events/{item_id}` |
| `list_recipes` | GET | `/api/recipes` |
| `list_recipes_bulk_actions_export` | GET | `/api/recipes/bulk-actions/export` |
| `list_recipes_bulk_actions_export_by_export_download` | GET | `/api/recipes/bulk-actions/export/{export_id}/download` |
| `list_recipes_by_slug_comments` | GET | `/api/recipes/{slug}/comments` |
| `list_recipes_by_slug_exports` | GET | `/api/recipes/{slug}/exports` |
| `list_recipes_exports` | GET | `/api/recipes/exports` |
| `list_recipes_shared_by_token_zip` | GET | `/api/recipes/shared/{token_id}/zip` |
| `list_recipes_suggestions` | GET | `/api/recipes/suggestions` |
| `list_recipes_timeline_events` | GET | `/api/recipes/timeline/events` |
| `patch_recipes` | PATCH | `/api/recipes` |
| `patch_recipes_by_slug` | PATCH | `/api/recipes/{slug}` |
| `patch_recipes_by_slug_last_made` | PATCH | `/api/recipes/{slug}/last-made` |
| `update_recipes` | PUT | `/api/recipes` |
| `update_recipes_by_slug` | PUT | `/api/recipes/{slug}` |
| `update_recipes_by_slug_image` | PUT | `/api/recipes/{slug}/image` |
| `update_recipes_timeline_events_by_item` | PUT | `/api/recipes/timeline/events/{item_id}` |
| `update_recipes_timeline_events_by_item_image` | PUT | `/api/recipes/timeline/events/{item_id}/image` |

## `shared` (4)

| tool | method | path |
|------|--------|------|
| `create_shared_recipes` | POST | `/api/shared/recipes` |
| `delete_shared_recipes_by_item` | DELETE | `/api/shared/recipes/{item_id}` |
| `get_shared_recipes_by_item` | GET | `/api/shared/recipes/{item_id}` |
| `list_shared_recipes` | GET | `/api/shared/recipes` |

## `units` (6)

| tool | method | path |
|------|--------|------|
| `create_units` | POST | `/api/units` |
| `delete_units_by_item` | DELETE | `/api/units/{item_id}` |
| `get_units_by_item` | GET | `/api/units/{item_id}` |
| `list_units` | GET | `/api/units` |
| `update_units_by_item` | PUT | `/api/units/{item_id}` |
| `update_units_merge` | PUT | `/api/units/merge` |

## `users` (17)

| tool | method | path |
|------|--------|------|
| `create_users_api_tokens` | POST | `/api/users/api-tokens` |
| `create_users_by_id_favorites_by_slug` | POST | `/api/users/{id}/favorites/{slug}` |
| `create_users_by_id_image` | POST | `/api/users/{id}/image` |
| `create_users_by_id_ratings_by_slug` | POST | `/api/users/{id}/ratings/{slug}` |
| `create_users_forgot_password` | POST | `/api/users/forgot-password` |
| `create_users_register` | POST | `/api/users/register` |
| `create_users_reset_password` | POST | `/api/users/reset-password` |
| `delete_users_api_tokens_by_token` | DELETE | `/api/users/api-tokens/{token_id}` |
| `delete_users_by_id_favorites_by_slug` | DELETE | `/api/users/{id}/favorites/{slug}` |
| `get_users_self_ratings_by_recipe` | GET | `/api/users/self/ratings/{recipe_id}` |
| `list_users_by_id_favorites` | GET | `/api/users/{id}/favorites` |
| `list_users_by_id_ratings` | GET | `/api/users/{id}/ratings` |
| `list_users_self` | GET | `/api/users/self` |
| `list_users_self_favorites` | GET | `/api/users/self/favorites` |
| `list_users_self_ratings` | GET | `/api/users/self/ratings` |
| `update_users_by_item` | PUT | `/api/users/{item_id}` |
| `update_users_password` | PUT | `/api/users/password` |

## `utils` (1)

| tool | method | path |
|------|--------|------|
| `list_utils_download` | GET | `/api/utils/download` |
