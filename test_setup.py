#!/usr/bin/env python3
"""
Test script to verify your fire detection setup
Run this before launching your Streamlit app
"""

import os
import sys

def main():
    print("🔥 Fire Detection Setup Verification")
    print("=" * 50)
    
    # Check Python version
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    
    # Check required files
    required_files = ['app.py', 'best.pt', 'requirements.txt']
    print(f"\n📁 Checking required files...")
    
    for file in required_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"✅ {file} - {size:,} bytes")
        else:
            print(f"❌ {file} - NOT FOUND")
    
    # Check model file specifically
    model_path = 'best.pt'
    if os.path.exists(model_path):
        size = os.path.getsize(model_path)
        if size < 1000:  # Less than 1KB is suspicious
            print(f"⚠️  WARNING: Model file is very small ({size} bytes)")
        elif size > 100_000_000:  # More than 100MB
            print(f"ℹ️  Large model file ({size/1_000_000:.1f} MB)")
    
    # Test package imports
    print(f"\n📦 Testing package imports...")
    
    packages = [
        ('streamlit', 'st'),
        ('ultralytics', 'YOLO'),
        ('cv2', 'cv2'),
        ('torch', 'torch')
    ]
    
    failed_imports = []
    
    for package_name, import_name in packages:
        try:
            if package_name == 'ultralytics':
                from ultralytics import YOLO
                print(f"✅ {package_name}")
            elif package_name == 'streamlit':
                import streamlit as st
                print(f"✅ {package_name} (v{st.__version__})")
            else:
                exec(f"import {import_name}")
                print(f"✅ {package_name}")
        except ImportError as e:
            print(f"❌ {package_name} - {e}")
            failed_imports.append(package_name)
    
    # Test model loading
    if 'ultralytics' not in failed_imports and os.path.exists('best.pt'):
        print(f"\n🤖 Testing YOLO model...")
        try:
            from ultralytics import YOLO
            model = YOLO('best.pt')
            print("✅ Model loaded successfully!")
            
            # Get model info
            try:
                classes = model.names
                print(f"✅ Model classes: {classes}")
                
                # Check for fire class
                fire_found = False
                for idx, name in classes.items():
                    if 'fire' in name.lower():
                        print(f"✅ Fire class found: '{name}' at index {idx}")
                        fire_found = True
                        break
                
                if not fire_found:
                    print("⚠️  No 'fire' class found. Available classes:")
                    for idx, name in classes.items():
                        print(f"   - {idx}: {name}")
                        
            except Exception as e:
                print(f"⚠️  Could not get model classes: {e}")
                
        except Exception as e:
            print(f"❌ Could not load model: {e}")
    
    # Test camera (if available)
    if 'cv2' not in failed_imports:
        print(f"\n📹 Testing camera access...")
        try:
            import cv2
            cap = cv2.VideoCapture(0)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    print(f"✅ Camera working! Frame shape: {frame.shape}")
                else:
                    print("⚠️  Camera opened but couldn't read frame")
                cap.release()
            else:
                print("⚠️  Could not open camera (normal if no camera available)")
        except Exception as e:
            print(f"❌ Camera test failed: {e}")
    
    # Summary
    print(f"\n" + "=" * 50)
    if failed_imports:
        print("❌ SETUP INCOMPLETE!")
        print(f"Missing packages: {', '.join(failed_imports)}")
        print("Run: pip install -r requirements.txt")
    else:
        print("🎉 SETUP LOOKS GOOD!")
        print("You can run: streamlit run app.py")
    
    print("=" * 50)

if __name__ == "__main__":
    main()