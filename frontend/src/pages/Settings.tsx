import React, { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const Settings: React.FC = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('profile');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Profile form state
  const [profileForm, setProfileForm] = useState({
    full_name: user?.full_name || '',
    email: user?.email || '',
    current_password: '',
    new_password: '',
    confirm_password: '',
  });

  // System settings state (admin only)
  const [systemSettings, setSystemSettings] = useState({
    court_name: 'District Court Management System',
    court_address: '123 Justice Street, Legal City, State 12345',
    contact_email: 'admin@dcm.gov.in',
    contact_phone: '+91-9876543210',
    working_hours_start: '09:00',
    working_hours_end: '17:00',
    case_number_prefix: 'DCM',
    auto_assign_cases: true,
    email_notifications: true,
    sms_notifications: false,
    backup_frequency: 'daily',
    session_timeout: '30',
  });

  const handleProfileSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);

    try {
      // Validate passwords if changing password
      if (profileForm.new_password) {
        if (profileForm.new_password !== profileForm.confirm_password) {
          throw new Error('New passwords do not match');
        }
        if (profileForm.new_password.length < 6) {
          throw new Error('Password must be at least 6 characters long');
        }
      }

      // Mock API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setMessage({ type: 'success', text: 'Profile updated successfully!' });
      
      // Clear password fields
      setProfileForm(prev => ({
        ...prev,
        current_password: '',
        new_password: '',
        confirm_password: '',
      }));
    } catch (error) {
      setMessage({ 
        type: 'error', 
        text: error instanceof Error ? error.message : 'Failed to update profile' 
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSystemSettingsSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);

    try {
      // Mock API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setMessage({ type: 'success', text: 'System settings updated successfully!' });
    } catch (error) {
      setMessage({ 
        type: 'error', 
        text: 'Failed to update system settings' 
      });
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'profile', name: 'Profile', icon: '👤' },
    ...(user?.role === 'admin' ? [
      { id: 'system', name: 'System Settings', icon: '⚙️' },
      { id: 'security', name: 'Security', icon: '🔒' },
      { id: 'backup', name: 'Backup & Restore', icon: '💾' },
    ] : []),
    { id: 'notifications', name: 'Notifications', icon: '🔔' },
  ];

  return (
    <div className="container mx-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Settings</h1>
      </div>

      {message && (
        <div className={`mb-6 p-4 rounded-md ${
          message.type === 'success' 
            ? 'bg-green-50 border border-green-200 text-green-800'
            : 'bg-red-50 border border-red-200 text-red-800'
        }`}>
          {message.text}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Navigation Tabs */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle>Settings Menu</CardTitle>
            </CardHeader>
            <CardContent>
              <nav className="space-y-2">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full text-left px-3 py-2 rounded-md transition-colors ${
                      activeTab === tab.id
                        ? 'bg-blue-100 text-blue-700'
                        : 'hover:bg-gray-100'
                    }`}
                  >
                    <span className="mr-2">{tab.icon}</span>
                    {tab.name}
                  </button>
                ))}
              </nav>
            </CardContent>
          </Card>
        </div>

        {/* Content Area */}
        <div className="lg:col-span-3">
          {activeTab === 'profile' && (
            <Card>
              <CardHeader>
                <CardTitle>Profile Settings</CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleProfileSubmit} className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Full Name
                      </label>
                      <Input
                        value={profileForm.full_name}
                        onChange={(e) => setProfileForm(prev => ({ ...prev, full_name: e.target.value }))}
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Email
                      </label>
                      <Input
                        type="email"
                        value={profileForm.email}
                        onChange={(e) => setProfileForm(prev => ({ ...prev, email: e.target.value }))}
                        required
                      />
                    </div>
                  </div>

                  <hr className="my-6" />
                  
                  <h3 className="text-lg font-medium">Change Password</h3>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Current Password
                    </label>
                    <Input
                      type="password"
                      value={profileForm.current_password}
                      onChange={(e) => setProfileForm(prev => ({ ...prev, current_password: e.target.value }))}
                    />
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        New Password
                      </label>
                      <Input
                        type="password"
                        value={profileForm.new_password}
                        onChange={(e) => setProfileForm(prev => ({ ...prev, new_password: e.target.value }))}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Confirm New Password
                      </label>
                      <Input
                        type="password"
                        value={profileForm.confirm_password}
                        onChange={(e) => setProfileForm(prev => ({ ...prev, confirm_password: e.target.value }))}
                      />
                    </div>
                  </div>

                  <Button type="submit" disabled={loading}>
                    {loading ? 'Updating...' : 'Update Profile'}
                  </Button>
                </form>
              </CardContent>
            </Card>
          )}

          {activeTab === 'system' && user?.role === 'admin' && (
            <Card>
              <CardHeader>
                <CardTitle>System Settings</CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSystemSettingsSubmit} className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Court Name
                      </label>
                      <Input
                        value={systemSettings.court_name}
                        onChange={(e) => setSystemSettings(prev => ({ ...prev, court_name: e.target.value }))}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Contact Email
                      </label>
                      <Input
                        type="email"
                        value={systemSettings.contact_email}
                        onChange={(e) => setSystemSettings(prev => ({ ...prev, contact_email: e.target.value }))}
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Court Address
                    </label>
                    <Input
                      value={systemSettings.court_address}
                      onChange={(e) => setSystemSettings(prev => ({ ...prev, court_address: e.target.value }))}
                    />
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Contact Phone
                      </label>
                      <Input
                        value={systemSettings.contact_phone}
                        onChange={(e) => setSystemSettings(prev => ({ ...prev, contact_phone: e.target.value }))}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Working Hours Start
                      </label>
                      <Input
                        type="time"
                        value={systemSettings.working_hours_start}
                        onChange={(e) => setSystemSettings(prev => ({ ...prev, working_hours_start: e.target.value }))}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Working Hours End
                      </label>
                      <Input
                        type="time"
                        value={systemSettings.working_hours_end}
                        onChange={(e) => setSystemSettings(prev => ({ ...prev, working_hours_end: e.target.value }))}
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Case Number Prefix
                      </label>
                      <Input
                        value={systemSettings.case_number_prefix}
                        onChange={(e) => setSystemSettings(prev => ({ ...prev, case_number_prefix: e.target.value }))}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Session Timeout (minutes)
                      </label>
                      <Input
                        type="number"
                        value={systemSettings.session_timeout}
                        onChange={(e) => setSystemSettings(prev => ({ ...prev, session_timeout: e.target.value }))}
                      />
                    </div>
                  </div>

                  <div className="space-y-3">
                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        id="auto_assign"
                        checked={systemSettings.auto_assign_cases}
                        onChange={(e) => setSystemSettings(prev => ({ ...prev, auto_assign_cases: e.target.checked }))}
                        className="mr-2"
                      />
                      <label htmlFor="auto_assign" className="text-sm font-medium text-gray-700">
                        Auto-assign cases to available clerks
                      </label>
                    </div>

                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        id="email_notifications"
                        checked={systemSettings.email_notifications}
                        onChange={(e) => setSystemSettings(prev => ({ ...prev, email_notifications: e.target.checked }))}
                        className="mr-2"
                      />
                      <label htmlFor="email_notifications" className="text-sm font-medium text-gray-700">
                        Enable email notifications
                      </label>
                    </div>

                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        id="sms_notifications"
                        checked={systemSettings.sms_notifications}
                        onChange={(e) => setSystemSettings(prev => ({ ...prev, sms_notifications: e.target.checked }))}
                        className="mr-2"
                      />
                      <label htmlFor="sms_notifications" className="text-sm font-medium text-gray-700">
                        Enable SMS notifications
                      </label>
                    </div>
                  </div>

                  <Button type="submit" disabled={loading}>
                    {loading ? 'Updating...' : 'Update System Settings'}
                  </Button>
                </form>
              </CardContent>
            </Card>
          )}

          {activeTab === 'notifications' && (
            <Card>
              <CardHeader>
                <CardTitle>Notification Preferences</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="space-y-3">
                    <h3 className="text-lg font-medium">Email Notifications</h3>
                    
                    <div className="space-y-2">
                      <div className="flex items-center">
                        <input type="checkbox" id="case_updates" defaultChecked className="mr-2" />
                        <label htmlFor="case_updates" className="text-sm">Case status updates</label>
                      </div>
                      
                      <div className="flex items-center">
                        <input type="checkbox" id="hearing_reminders" defaultChecked className="mr-2" />
                        <label htmlFor="hearing_reminders" className="text-sm">Hearing reminders</label>
                      </div>
                      
                      <div className="flex items-center">
                        <input type="checkbox" id="new_assignments" defaultChecked className="mr-2" />
                        <label htmlFor="new_assignments" className="text-sm">New case assignments</label>
                      </div>
                      
                      <div className="flex items-center">
                        <input type="checkbox" id="system_alerts" className="mr-2" />
                        <label htmlFor="system_alerts" className="text-sm">System maintenance alerts</label>
                      </div>
                    </div>
                  </div>

                  <hr />

                  <div className="space-y-3">
                    <h3 className="text-lg font-medium">SMS Notifications</h3>
                    
                    <div className="space-y-2">
                      <div className="flex items-center">
                        <input type="checkbox" id="urgent_alerts" defaultChecked className="mr-2" />
                        <label htmlFor="urgent_alerts" className="text-sm">Urgent case alerts</label>
                      </div>
                      
                      <div className="flex items-center">
                        <input type="checkbox" id="hearing_sms" className="mr-2" />
                        <label htmlFor="hearing_sms" className="text-sm">Hearing reminders via SMS</label>
                      </div>
                    </div>
                  </div>

                  <Button>Save Notification Preferences</Button>
                </div>
              </CardContent>
            </Card>
          )}

          {activeTab === 'security' && user?.role === 'admin' && (
            <Card>
              <CardHeader>
                <CardTitle>Security Settings</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  <div>
                    <h3 className="text-lg font-medium mb-3">Password Policy</h3>
                    <div className="space-y-2">
                      <div className="flex items-center">
                        <input type="checkbox" id="min_length" defaultChecked className="mr-2" />
                        <label htmlFor="min_length" className="text-sm">Minimum 8 characters</label>
                      </div>
                      <div className="flex items-center">
                        <input type="checkbox" id="require_numbers" defaultChecked className="mr-2" />
                        <label htmlFor="require_numbers" className="text-sm">Require numbers</label>
                      </div>
                      <div className="flex items-center">
                        <input type="checkbox" id="require_special" className="mr-2" />
                        <label htmlFor="require_special" className="text-sm">Require special characters</label>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-lg font-medium mb-3">Session Management</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Session Timeout (minutes)
                        </label>
                        <Input type="number" defaultValue="30" />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Max Login Attempts
                        </label>
                        <Input type="number" defaultValue="5" />
                      </div>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-lg font-medium mb-3">Two-Factor Authentication</h3>
                    <div className="space-y-2">
                      <div className="flex items-center">
                        <input type="checkbox" id="enable_2fa" className="mr-2" />
                        <label htmlFor="enable_2fa" className="text-sm">Enable 2FA for all users</label>
                      </div>
                      <div className="flex items-center">
                        <input type="checkbox" id="require_2fa_admin" defaultChecked className="mr-2" />
                        <label htmlFor="require_2fa_admin" className="text-sm">Require 2FA for administrators</label>
                      </div>
                    </div>
                  </div>

                  <Button>Update Security Settings</Button>
                </div>
              </CardContent>
            </Card>
          )}

          {activeTab === 'backup' && user?.role === 'admin' && (
            <Card>
              <CardHeader>
                <CardTitle>Backup & Restore</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  <div>
                    <h3 className="text-lg font-medium mb-3">Automatic Backups</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Backup Frequency
                        </label>
                        <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                          <option value="daily">Daily</option>
                          <option value="weekly">Weekly</option>
                          <option value="monthly">Monthly</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Retention Period (days)
                        </label>
                        <Input type="number" defaultValue="30" />
                      </div>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-lg font-medium mb-3">Manual Operations</h3>
                    <div className="flex gap-4">
                      <Button>Create Backup Now</Button>
                      <Button variant="outline">Download Latest Backup</Button>
                      <Button variant="outline">Restore from Backup</Button>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-lg font-medium mb-3">Recent Backups</h3>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between p-3 border rounded-md">
                        <div>
                          <div className="font-medium">Daily Backup - August 30, 2024</div>
                          <div className="text-sm text-gray-600">Size: 2.3 GB</div>
                        </div>
                        <Button variant="outline" size="sm">Download</Button>
                      </div>
                      <div className="flex items-center justify-between p-3 border rounded-md">
                        <div>
                          <div className="font-medium">Daily Backup - August 29, 2024</div>
                          <div className="text-sm text-gray-600">Size: 2.2 GB</div>
                        </div>
                        <Button variant="outline" size="sm">Download</Button>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default Settings;
