# Supabase Storage Setup Guide for Ticket Attachments

## ⚠️ IMPORTANT: Complete These Steps Before Testing

### Step 1: Create Storage Bucket in Supabase

1. **Go to Supabase Dashboard**: https://supabase.com/dashboard
2. **Select your UniHelp project**
3. **Navigate to Storage**: Click "Storage" in left sidebar
4. **Create New Bucket**:
   - Click "New bucket"
   - **Bucket name**: `ticket-attachments` (exact name required)
   - **Public**: ✅ Check this box (makes files publicly accessible)
   - **File size limit**: `5242880` bytes (5MB - matches our validation)
   - Click "Create bucket"

### Step 2: Configure Bucket Policies

By default, the bucket should allow public uploads and reads. If you want to add security:

```sql
-- Allow authenticated users to upload files
CREATE POLICY "Allow authenticated uploads"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (bucket_id = 'ticket-attachments');

-- Allow public read access
CREATE POLICY "Allow public read access"
ON storage.objects FOR SELECT
TO public
USING (bucket_id = 'ticket-attachments');
```

### Step 3: Verify Storage Access

After creating the bucket:

1. **Check bucket exists**: You should see `ticket-attachments` in Storage list
2. **Verify it's public**: Globe icon should be visible
3. **Test permissions**: The bucket should accept uploads from your app

### Step 4: Update Database Schema (Optional)

The `ticket` table already has a `filepath` column which will now store:
```
supabase://ticket-attachments/tickets/2026/03/16/20260316_143021_image.png
```

No database migration needed! ✅

---

## 🧪 Testing the Upload Feature

### Test Checklist:

1. **Upload a small image** (< 1MB):
   - Should succeed ✅
   - See green success message
   - File appears in Supabase Storage bucket

2. **Upload a large image** (> 5MB):
   - Should fail with "File too large" error ❌

3. **Upload invalid file type** (.pdf, .doc):
   - Should fail with "Invalid file type" error ❌

4. **View ticket with attachment**:
   - Image should display properly
   - Download link should work

---

## 🔍 Troubleshooting

### Error: "Bucket not found"
**Solution**: Make sure you created the bucket with exact name `ticket-attachments`

### Error: "Permission denied"
**Solution**: Ensure bucket is set to PUBLIC or add proper RLS policies

### Error: "Upload failed"
**Solution**: Check Supabase logs at: https://supabase.com/dashboard/project/{your-project}/logs

### Files not showing in ticket view
**Solution**: The `public_url` returned from upload should be stored/displayed properly

---

## 📊 How It Works Now

### Upload Flow:
```
User selects image → JavaScript validates → AJAX POST → 
Flask receives file → Validates again → Reads file data → 
Uploads to Supabase Storage → Gets public URL → 
Returns JSON with supabase:// filepath → 
Stores in database → User sees success message
```

### File Storage Structure:
```
Supabase Storage: ticket-attachments/
├── tickets/
│   ├── 2026/
│   │   ├── 03/
│   │   │   ├── 16/
│   │   │   │   ├── 20260316_143021_image.png
│   │   │   │   └── 20260316_144532_screenshot.jpg
│   │   │   └── 17/
│   │   └── 04/
```

### Database Storage:
```sql
ticket.filepath = 'supabase://ticket-attachments/tickets/2026/03/16/20260316_143021_image.png'
```

### File Access:
When viewing ticket:
- Frontend reads `filepath` from database
- Extracts bucket and path from `supabase://` URL
- Fetches public URL from Supabase Storage
- Displays image or provides download link

---

## 🎯 Benefits of Supabase Storage

| Feature | Local Storage (Old) | Supabase Storage (New) |
|---------|---------------------|------------------------|
| **Vercel Compatible** | ❌ No (ephemeral) | ✅ Yes (permanent) |
| **Scalability** | Limited by disk | Unlimited cloud storage |
| **CDN** | ❌ No | ✅ Built-in CDN |
| **Backups** | Manual | Automatic via Supabase |
| **Access Speed** | Server-dependent | Global CDN edges |
| **Deployment** | Files lost on redeploy | Files persist forever |
| **Security** | Filesystem permissions | RLS policies |

---

## 📝 Environment Variables

No new environment variables needed! The existing Supabase credentials are used:
- `SUPABASE_URL`
- `SUPABASE_KEY` or `SUPABASE_SERVICE_KEY`

---

## 🚀 Deployment Status

✅ Code committed to GitHub  
✅ Pushed to Vercel  
⏳ Waiting for deployment  

Once Vercel deploys, complete Step 1-2 above in Supabase Dashboard, then test!

---

## Next Steps

1. **Wait for Vercel deployment** (~1-2 minutes)
2. **Create `ticket-attachments` bucket** in Supabase Dashboard
3. **Set bucket to PUBLIC**
4. **Test file upload** with a small image
5. **Verify file appears** in Supabase Storage
6. **Check ticket view** shows uploaded image

---

**Questions?** Check Supabase docs: https://supabase.com/docs/guides/storage
