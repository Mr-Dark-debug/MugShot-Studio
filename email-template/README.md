# Email Templates

This directory contains HTML email templates for Supabase authentication emails. All templates use the MugShot Studio brand colors and consistent styling.

## Templates

### Standard Templates
1. **confirmation.html** - Email confirmation for new signups
2. **invitation.html** - Invitation emails for new users
3. **magic-link.html** - Magic link login emails
4. **email-change.html** - Email change confirmation
5. **reset-password.html** - Password reset emails
6. **reauthentication.html** - Reauthentication code emails

### Enhanced Templates (Recommended)
1. **enhanced-confirmation.html** - Enhanced email confirmation with better visuals
2. **enhanced-invitation.html** - Enhanced invitation emails with improved design
3. **enhanced-magic-link.html** - Enhanced magic link login with better styling
4. **enhanced-email-change.html** - Enhanced email change confirmation with security notices
5. **enhanced-reset-password.html** - Enhanced password reset with security tips
6. **enhanced-reauthentication.html** - Enhanced reauthentication with improved code display

## Brand Colors

- Primary Teal: `#0f7d70` (used for headers, buttons, and links)
- Background: `#F4F5F5` (light gray background)
- Content: White cards with subtle shadows
- Text: Dark gray (`#333`) for content, white for headers

## Design Features

The enhanced templates include:

- Modern gradient headers with subtle patterns
- Custom SVG illustrations for each email type
- Improved typography with better spacing and readability
- Enhanced buttons with hover effects and shadows
- Informational boxes for security notices and tips
- Better code display for authentication tokens
- Social media links in the footer
- Company address and complete copyright information

## Supabase Variables

All templates use Supabase's standard template variables:

- `{{ .ConfirmationURL }}` - Confirmation link
- `{{ .SiteURL }}` - Site URL
- `{{ .Email }}` - Current email address
- `{{ .NewEmail }}` - New email address
- `{{ .Token }}` - Reauthentication token

## Usage

To use these templates with Supabase:

1. Choose between standard or enhanced templates
2. Copy the HTML content of each template
3. Paste into the corresponding email template section in your Supabase dashboard
4. The templates will automatically populate with the correct variables when emails are sent

## Customization

To customize these templates:

1. Adjust the color values in the `<style>` section
2. Modify the header text or branding
3. Update the footer copyright information
4. Adjust spacing or typography as needed
5. Replace SVG illustrations with your own icons
6. Modify social media links to point to your accounts

All templates are designed to be responsive and work across all major email clients.