- UserProfile.mentor is calculated

- script commands/set_mentor_to_current_pro: 

- setting Elizabeth as default pro is causing problem

- history of pro changes

- cse@duprenunnelly.com does not have a user profile, should it be manually created?


Pro relationship fix:

1. If a taster is invited and they don't have a current_pro, the party pro gets assigned 
		main/forms.py : PartyInviteTasterForm : clean

2. If a taster or host orders VIP, their pro changes
	TODO: Not sure what happens when a pro orders VIP
	TODO: Also currently it's not checking whether a user ordered 7 days within the party window

		main/views.py : order_complete : line 841

3. If a host has never been assigned to pro, the pro setting up the party gets added as current_pro

		main/views.py : party_add : line 1169

4. Host link/unlink, Taster link/unlink pros are enabled

		accounts/views.py : pro_unlink, pro_link updated

5. Updated make_pro and make_host to link to the right pros and use the right variables in userprofile
		
		accounts/views.py : make_pro_host, sign_up : used mentor and current_pro