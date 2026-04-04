import sys
user = env['res.users'].search([('login', 'in', ['f20240248@dubai.bits-pilani.ac.in', 'admin', 'aadit'])])
if user:
    user.write({'password': 'admin'})
    env.cr.commit()
    print(f"Successfully reset password to 'admin' for users: {user.mapped('login')}")
else:
    print("Could not find the user!")
